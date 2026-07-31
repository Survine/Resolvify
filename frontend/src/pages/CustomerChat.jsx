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
import { MessageSquare, Sun, Moon, AlertCircle } from 'lucide-react'

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

  useEffect(() => {
    api.get('/chat/shops/')
      .then((res) => setShops(res.data))
      .catch((err) => console.error('Error fetching shops:', err))
      .finally(() => setLoadingShops(false))
  }, [])

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, agentTyping])

  // Setup WebSocket connection
  const { send } = useWebSocket(email ? `/chat/ws/customer/${email}` : null, {
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
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            message: data.message,
            is_from_customer: data.from === 'customer',
            created_at: data.timestamp || new Date().toISOString(),
            employee: data.from === 'support' ? { first_name: data.agent_name || 'Support Agent', last_name: '' } : null,
          },
        ])
      } else if (data.type === 'agent_assigned') {
        setAgentName(data.agent_name || 'Support Agent')
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            message: `${data.agent_name || 'Support Agent'} has joined the chat.`,
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
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            message: 'This support session has been closed. Thank you!',
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
      // 1. Ensure customer is created
      await api.post(`/customers/`, { name, email })
    } catch (err) {
      if (err.response?.status !== 400) { // status 400 means already registered, which is fine
        setError('Failed to register customer details. Please try again.')
        setConnecting(false)
        return
      }
    }

    try {
      // 2. Create Chat Session
      const sessionRes = await api.post(`/chat/sessions/?customer_email=${encodeURIComponent(email)}&shop_id=${selectedShop}`)
      setSession(sessionRes.data)
      setMessages([
        {
          id: Date.now(),
          message: 'Hello! I need assistance.',
          is_from_customer: true,
          created_at: new Date().toISOString(),
        },
      ])
    } catch (err) {
      console.error(err)
      setError('Failed to initiate chat session. Please verify connection.')
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

  return (
    <div className="min-h-screen flex flex-col bg-[hsl(var(--bg-secondary))] overflow-hidden">
      {/* Header */}
      <header className="p-4 border-b border-[hsl(var(--border))] bg-[hsl(var(--surface))] flex items-center justify-between shadow-sm shrink-0">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-[hsl(var(--brand))]" />
          <span className="font-bold text-base tracking-tight">Resolvify Customer Support</span>
        </div>
        <div className="flex items-center gap-3">
          {session && (
            <Badge color={connected ? 'green' : 'red'} dot>
              {connected ? 'Connected' : 'Disconnected'}
            </Badge>
          )}
          <Button variant="ghost" size="sm" onClick={toggle} className="p-2 rounded-full">
            {dark ? <Sun className="w-4.5 h-4.5" /> : <Moon className="w-4.5 h-4.5" />}
          </Button>
        </div>
      </header>

      {/* Main chat interface */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-6 overflow-hidden">
        {!session ? (
          /* Welcome & setup form */
          <div className="w-full max-w-md bg-[hsl(var(--surface))] rounded-2xl border border-[hsl(var(--border))] p-8 shadow-lg space-y-6 animate-slide-up">
            <div className="text-center space-y-2">
              <h1 className="text-2xl font-bold tracking-tight">How can we help?</h1>
              <p className="text-sm text-[hsl(var(--text-secondary))]">Enter details below to start a live chat session</p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-[var(--radius)] flex items-start gap-2 text-sm text-[hsl(var(--danger))]">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleStartChat} className="space-y-4">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-[hsl(var(--text-secondary))]">Select Location</label>
                <select
                  value={selectedShop}
                  onChange={(e) => setSelectedShop(e.target.value)}
                  required
                  disabled={loadingShops}
                  className="w-full px-3.5 py-2.5 rounded-[var(--radius)] border border-[hsl(var(--border))] bg-[hsl(var(--surface))] text-[hsl(var(--text-primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--brand))]"
                >
                  <option value="">{loadingShops ? 'Loading locations...' : 'Choose a shop...'}</option>
                  {shops.map((shop) => (
                    <option key={shop.id} value={shop.id}>{shop.name} {shop.location ? `(${shop.location})` : ''}</option>
                  ))}
                </select>
              </div>

              <Input
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                required
              />

              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />

              <Button type="submit" loading={connecting} className="w-full py-2.5">
                Start Live Chat
              </Button>
            </form>
          </div>
        ) : (
          /* Live Chat conversation */
          <div className="w-full max-w-2xl h-[80vh] bg-[hsl(var(--surface))] rounded-2xl border border-[hsl(var(--border))] shadow-lg flex flex-col overflow-hidden animate-fade-in">
            {/* Session Info banner */}
            <div className="px-4 py-3 bg-[hsl(var(--bg-tertiary))] border-b border-[hsl(var(--border))] flex items-center justify-between text-xs text-[hsl(var(--text-secondary))] shrink-0">
              <span>Connected to: <span className="font-semibold text-[hsl(var(--text-primary))]">{shops.find(s => s.id === parseInt(selectedShop))?.name}</span></span>
              <span>Session ID: #{session.id}</span>
            </div>

            {/* Chat message body */}
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 flex flex-col bg-[hsl(var(--bg-secondary))]">
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id || msg.timestamp}
                  message={msg}
                  isSelf={msg.is_from_customer}
                />
              ))}
              {agentTyping && <TypingIndicator name={agentName} className="self-start" />}
            </div>

            {/* Input area */}
            <MessageInput
              onSend={handleSendMessage}
              onTyping={handleTyping}
              disabled={!connected}
            />
          </div>
        )}
      </main>
    </div>
  )
}
