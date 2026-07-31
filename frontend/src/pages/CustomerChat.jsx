import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { useTheme } from '../hooks/useTheme'
import api from '../api/client'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import MessageBubble from '../components/chat/MessageBubble'
import MessageInput from '../components/chat/MessageInput'
import TypingIndicator from '../components/chat/TypingIndicator'
import { MessageSquare, Sun, Moon, AlertCircle, Sparkles, MapPin, RefreshCw, XCircle } from 'lucide-react'

const SESSION_STORAGE_KEY = 'resolvify_customer_session'

const QUICK_SUGGESTIONS = [
  '📦 I need help with an order status',
  '🏬 What are your store opening hours?',
  '💳 I have a question about billing/invoice',
  '👨‍💻 Connect me with a live support agent',
]

export default function CustomerChat() {
  const { dark, toggle } = useTheme()
  const [shops, setShops] = useState([])
  const [selectedShop, setSelectedShop] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  
  const [connected, setConnected] = useState(false)
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [agentTyping, setAgentTyping] = useState(false)
  const [agentName, setAgentName] = useState('Support Agent')
  
  const [loadingShops, setLoadingShops] = useState(true)
  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState('')

  const chatContainerRef = useRef(null)
  const typingTimeoutRef = useRef(null)

  // 1. Fetch available shops
  useEffect(() => {
    api.get('/chat/shops/')
      .then((res) => setShops(res.data))
      .catch((err) => console.error('Error fetching shops:', err))
      .finally(() => setLoadingShops(false))
  }, [])

  // 2. Restore persistent customer session on refresh
  useEffect(() => {
    const saved = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!saved) return

    try {
      const parsed = JSON.parse(saved)
      if (!parsed.session?.id || !parsed.email) return

      api.get(`/chat/sessions/${parsed.session.id}`)
        .then(async (res) => {
          if (res.data.status === 'closed') {
            localStorage.removeItem(SESSION_STORAGE_KEY)
            return
          }

          setSession(res.data)
          setEmail(parsed.email)
          setName(parsed.name || '')
          setSelectedShop(parsed.selectedShop || res.data.shop_id)

          // Fetch message history for restored session
          try {
            const msgRes = await api.get(`/chat/sessions/${parsed.session.id}/messages`)
            if (msgRes.data && msgRes.data.length > 0) {
              setMessages(
                msgRes.data.map((m) => ({
                  id: m.id,
                  message: m.message,
                  is_from_customer: m.is_from_customer,
                  created_at: m.created_at,
                  employee: m.employee
                    ? { first_name: m.employee.first_name, last_name: m.employee.last_name }
                    : m.employee_id
                    ? { first_name: 'Support Agent', last_name: '' }
                    : null,
                }))
              )
            }
          } catch (mErr) {
            console.error('Error fetching session messages:', mErr)
          }
        })
        .catch(() => {
          localStorage.removeItem(SESSION_STORAGE_KEY)
        })
    } catch {
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }, [])

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, agentTyping])

  // 3. WebSocket connection setup
  const { send } = useWebSocket(email ? `/chat/ws/customer/${encodeURIComponent(email)}` : null, {
    enabled: !!email && !!session,
    onOpen: () => {
      setConnected(true)
      setConnecting(false)
    },
    onClose: () => {
      setConnected(false)
    },
    onMessage: (data) => {
      if (data.type === 'message') {
        if (data.from === 'support' && data.agent_name) {
          setAgentName(data.agent_name)
        }
        setMessages((prev) => {
          const isDup = prev.some(
            (m) =>
              m.message === data.message &&
              m.is_from_customer === (data.from === 'customer') &&
              (m.id === data.id || Math.abs(new Date(m.created_at) - new Date(data.timestamp || new Date())) < 2000)
          )
          if (isDup) return prev

          return [
            ...prev,
            {
              id: data.id || Date.now(),
              message: data.message,
              is_from_customer: data.from === 'customer',
              created_at: data.timestamp || new Date().toISOString(),
              employee: data.from === 'support' ? { first_name: data.agent_name || 'Support Agent', last_name: '' } : null,
            },
          ]
        })
      } else if (data.type === 'agent_assigned') {
        setAgentName(data.agent_name || 'Support Agent')
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            message: `🎉 Agent ${data.agent_name || 'Support Specialist'} has joined the chat session!`,
            is_from_customer: false,
            created_at: new Date().toISOString(),
            employee: { first_name: 'System', last_name: '' },
          },
        ])
      } else if (data.type === 'typing') {
        setAgentTyping(true)
        if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
        typingTimeoutRef.current = setTimeout(() => setAgentTyping(false), 3000)
      } else if (data.type === 'stop_typing') {
        setAgentTyping(false)
      } else if (data.type === 'session_closed') {
        setConnected(false)
        setSession(null)
        localStorage.removeItem(SESSION_STORAGE_KEY)
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            message: 'This support session has been concluded. Thank you for reaching out!',
            is_from_customer: false,
            created_at: new Date().toISOString(),
            employee: { first_name: 'System', last_name: '' },
          },
        ])
      }
    },
  })

  const handleStartChat = async (e) => {
    e.preventDefault()
    if (!selectedShop || !name.trim() || !email.trim()) return
    setConnecting(true)
    setError('')

    try {
      await api.post(`/customers/`, { name, email })
    } catch (err) {
      if (err.response?.status !== 400) {
        setError('Failed to register customer details. Please try again.')
        setConnecting(false)
        return
      }
    }

    try {
      const initialMessage = 'Hello! I need live support assistance.'
      const sessionRes = await api.post(
        `/chat/sessions/?customer_email=${encodeURIComponent(email)}&shop_id=${selectedShop}&initial_message=${encodeURIComponent(initialMessage)}`
      )
      const newSession = sessionRes.data

      setSession(newSession)
      setConnected(true)
      
      localStorage.setItem(
        SESSION_STORAGE_KEY,
        JSON.stringify({ session: newSession, email, name, selectedShop })
      )

      setMessages([
        {
          id: Date.now(),
          message: initialMessage,
          is_from_customer: true,
          created_at: new Date().toISOString(),
        },
      ])
    } catch (err) {
      console.error(err)
      setError('Failed to initiate chat session. Please verify server connection.')
      setConnecting(false)
    }
  }

  const handleSendMessage = (text) => {
    if (!session) return
    const timestamp = new Date().toISOString()
    send({
      type: 'chat_message',
      session_id: session.id,
      message: text,
      timestamp,
    })
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        message: text,
        is_from_customer: true,
        created_at: timestamp,
      },
    ])
  }

  const handleTyping = (isTyping) => {
    if (!session) return
    send({
      type: isTyping ? 'typing' : 'stop_typing',
      session_id: session.id,
    })
  }

  const handleEndChat = () => {
    localStorage.removeItem(SESSION_STORAGE_KEY)
    setSession(null)
    setConnected(false)
    setMessages([])
  }

  const currentShopObj = shops.find((s) => s.id === parseInt(selectedShop))

  return (
    <div className="h-screen w-screen flex flex-col bg-gradient-to-b from-[hsl(var(--bg-secondary))] to-[hsl(var(--bg-primary))] overflow-hidden antialiased">
      {/* Premium Header */}
      <header className="px-5 py-3.5 border-b border-[hsl(var(--border))] bg-[hsl(var(--surface))/80] backdrop-blur-md flex items-center justify-between shadow-xs shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-[hsl(var(--text-primary))] flex items-center gap-2">
              Resolvify Help Center
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wider font-semibold bg-blue-100 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800/50">
                Live Support
              </span>
            </h1>
            <p className="text-xs text-[hsl(var(--text-muted))]">Instant Resolution Desk</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {session && (
            <div className="flex items-center gap-2">
              <Badge color={connected ? 'green' : 'amber'} dot>
                {connected ? 'Connected' : 'Connecting...'}
              </Badge>
              <button
                onClick={handleEndChat}
                className="text-xs font-medium text-[hsl(var(--text-muted))] hover:text-red-500 transition-colors flex items-center gap-1 px-2.5 py-1 rounded-lg border border-[hsl(var(--border))] hover:border-red-200 cursor-pointer"
                title="End current chat session"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">End Session</span>
              </button>
            </div>
          )}
          <Button variant="ghost" size="sm" onClick={toggle} className="p-2 rounded-xl">
            {dark ? <Sun className="w-4.5 h-4.5" /> : <Moon className="w-4.5 h-4.5" />}
          </Button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 flex items-center justify-center p-3 sm:p-6 overflow-hidden">
        {!session ? (
          /* Welcome Card */
          <div className="w-full max-w-lg bg-[hsl(var(--surface))] rounded-3xl border border-[hsl(var(--border))] p-6 sm:p-8 shadow-2xl space-y-6 animate-slide-up backdrop-blur-xl">
            <div className="text-center space-y-2">
              <div className="inline-flex p-3 rounded-2xl bg-blue-50 dark:bg-blue-950/30 text-[hsl(var(--brand))] mb-1">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <h2 className="text-2xl font-extrabold tracking-tight text-[hsl(var(--text-primary))]">Start a Conversation</h2>
              <p className="text-sm text-[hsl(var(--text-secondary))]">Choose a branch location and enter your details to connect with a specialist</p>
            </div>

            {error && (
              <div className="p-3.5 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-2xl flex items-start gap-2.5 text-xs sm:text-sm text-[hsl(var(--danger))] animate-shake">
                <AlertCircle className="w-4.5 h-4.5 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleStartChat} className="space-y-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-[hsl(var(--text-secondary))] flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-[hsl(var(--brand))]" />
                  Select Branch Location
                </label>
                <select
                  value={selectedShop}
                  onChange={(e) => setSelectedShop(e.target.value)}
                  required
                  disabled={loadingShops}
                  className="w-full px-4 py-3 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--bg-secondary))] text-sm text-[hsl(var(--text-primary))] font-medium focus:outline-none focus:ring-2 focus:ring-[hsl(var(--brand))/30] transition-all cursor-pointer"
                >
                  <option value="">{loadingShops ? 'Loading shop locations...' : '-- Select Branch --'}</option>
                  {shops.map((shop) => (
                    <option key={shop.id} value={shop.id}>
                      {shop.name} {shop.location ? `— ${shop.location}` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <Input
                label="Your Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Hriday Bardhan"
                required
              />

              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. hriday@example.com"
                required
              />

              <Button
                type="submit"
                loading={connecting}
                className="w-full py-3.5 text-sm font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/20 text-white transform active:scale-98 transition-all cursor-pointer"
              >
                Connect to Live Agent
              </Button>
            </form>
          </div>
        ) : (
          /* Live Chat Experience */
          <div className="w-full max-w-3xl h-[88vh] bg-[hsl(var(--surface))] rounded-3xl border border-[hsl(var(--border))] shadow-2xl flex flex-col overflow-hidden animate-fade-in">
            {/* Active Session Sub-Header */}
            <div className="px-5 py-3 bg-[hsl(var(--bg-tertiary))] border-b border-[hsl(var(--border))] flex items-center justify-between text-xs text-[hsl(var(--text-secondary))] shrink-0 font-medium">
              <div className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-[hsl(var(--brand))]" />
                <span>
                  Branch: <span className="font-semibold text-[hsl(var(--text-primary))]">{currentShopObj?.name || 'Agartala Branch'}</span>
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="bg-[hsl(var(--surface))] px-2.5 py-1 rounded-md border border-[hsl(var(--border))] font-mono text-[11px]">
                  Session #{session.id}
                </span>
              </div>
            </div>

            {/* Chat Message Scrollable Container */}
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 flex flex-col bg-[hsl(var(--bg-secondary))] scroll-smooth">
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id || msg.created_at}
                  message={msg}
                  isSelf={msg.is_from_customer}
                />
              ))}

              {agentTyping && <TypingIndicator name={agentName} className="self-start" />}

              {/* Quick suggestion chips when messages are few */}
              {messages.length <= 2 && (
                <div className="mt-4 pt-4 border-t border-[hsl(var(--border))/50] space-y-2 animate-fade-in">
                  <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Quick Prompts:</p>
                  <div className="flex flex-wrap gap-2">
                    {QUICK_SUGGESTIONS.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(prompt)}
                        className="text-xs font-medium px-3 py-1.5 rounded-full bg-[hsl(var(--surface))] hover:bg-[hsl(var(--brand))/10] text-[hsl(var(--text-secondary))] hover:text-[hsl(var(--brand))] border border-[hsl(var(--border))] hover:border-[hsl(var(--brand))/30] transition-all cursor-pointer shadow-xs text-left"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Input Box */}
            <MessageInput
              onSend={handleSendMessage}
              onTyping={handleTyping}
              disabled={false}
            />
          </div>
        )}
      </main>
    </div>
  )
}
