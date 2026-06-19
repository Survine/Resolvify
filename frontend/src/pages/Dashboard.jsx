import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useWebSocket } from '../hooks/useWebSocket'
import Navbar from '../components/Navbar'
import SessionList from '../components/chat/SessionList'
import ChatWindow from '../components/chat/ChatWindow'
import api from '../api/client'
import { RefreshCw } from 'lucide-react'
import Button from '../components/ui/Button'

export default function Dashboard() {
  const { employee } = useAuth()
  const [waitingSessions, setWaitingSessions] = useState([])
  const [activeSessions, setActiveSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [customerTyping, setCustomerTyping] = useState(false)
  const typingTimeoutRef = useRef(null)

  // Fetch all sessions
  const fetchSessions = async () => {
    try {
      const [waitingRes, activeRes] = await Promise.all([
        api.get('/chat/sessions/waiting'),
        api.get('/chat/sessions/active'),
      ])
      setWaitingSessions(waitingRes.data)
      setActiveSessions(activeRes.data)
    } catch (err) {
      console.error('Error fetching sessions:', err)
    }
  }

  // Fetch messages for a specific session
  const fetchMessages = async (sessionId) => {
    try {
      const res = await api.get(`/chat/sessions/${sessionId}`)
      setMessages(res.data.messages || [])
    } catch (err) {
      console.error('Error fetching messages:', err)
    }
  }

  useEffect(() => {
    fetchSessions()
  }, [])

  // Setup WebSocket connection
  const { send } = useWebSocket(`/chat/ws/employee/${employee?.id}`, {
    enabled: !!employee?.id,
    onMessage: (data) => {
      if (data.type === 'new_session') {
        fetchSessions()
        showNotification('New support session request!')
      } else if (data.type === 'message') {
        if (currentSession && data.session_id === currentSession.id) {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now(),
              message: data.message,
              is_from_customer: data.from === 'customer',
              created_at: data.timestamp || new Date().toISOString(),
              employee: data.from === 'support' ? { first_name: data.agent_name, last_name: '' } : null,
            },
          ])
        } else {
          fetchSessions()
        }
      } else if (data.type === 'typing') {
        if (currentSession && data.session_id === currentSession.id) {
          setCustomerTyping(true)
          if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
          typingTimeoutRef.current = setTimeout(() => setCustomerTyping(false), 3000)
        }
      } else if (data.type === 'stop_typing') {
        if (currentSession && data.session_id === currentSession.id) {
          setCustomerTyping(false)
        }
      } else if (data.type === 'session_closed') {
        fetchSessions()
        if (currentSession && currentSession.id === data.session_id) {
          setCurrentSession(null)
          setMessages([])
          setCustomerTyping(false)
        }
      }
    },
  })

  const showNotification = (text) => {
    if (Notification.permission === 'granted') {
      new Notification('Resolvify', { body: text })
    }
  }

  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  const handleSelectSession = (session) => {
    setCurrentSession(session)
    setCustomerTyping(false)
    fetchMessages(session.id)
  }

  const handleSendMessage = (text) => {
    if (!currentSession) return
    const timestamp = new Date().toISOString()
    send({
      type: 'chat_message',
      session_id: currentSession.id,
      message: text,
      timestamp,
    })
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        message: text,
        is_from_customer: false,
        created_at: timestamp,
        employee: { first_name: employee.first_name, last_name: employee.last_name },
      },
    ])
  }

  const handleTyping = (isTyping) => {
    if (!currentSession) return
    send({
      type: isTyping ? 'typing' : 'stop_typing',
      session_id: currentSession.id,
    })
  }

  const handleAssign = async (sessionId) => {
    try {
      await api.put(`/chat/sessions/${sessionId}/assign`)
      await fetchSessions()
      const welcome = `Hello! I'm ${employee.first_name}. How can I assist you today?`
      send({
        type: 'chat_message',
        session_id: sessionId,
        message: welcome,
        timestamp: new Date().toISOString(),
      })
      // Fetch session object from updated list
      const updatedRes = await api.get(`/chat/sessions/${sessionId}`)
      setCurrentSession(updatedRes.data)
      setMessages(updatedRes.data.messages || [])
    } catch (err) {
      console.error('Error assigning session:', err)
    }
  }

  const handleCloseSession = async (sessionId) => {
    if (!confirm('Are you sure you want to end this chat session?')) return
    try {
      await api.put(`/chat/sessions/${sessionId}/close`)
      setCurrentSession(null)
      setMessages([])
      setCustomerTyping(false)
      fetchSessions()
    } catch (err) {
      console.error('Error closing session:', err)
    }
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-[hsl(var(--bg-primary))]">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 border-r border-[hsl(var(--border))] bg-[hsl(var(--surface))] flex flex-col shrink-0">
          <div className="p-4 border-b border-[hsl(var(--border))] flex items-center justify-between">
            <span className="font-bold text-sm">Chats</span>
            <Button variant="ghost" size="sm" onClick={fetchSessions} className="p-1 rounded-full">
              <RefreshCw className="w-4 h-4 text-[hsl(var(--text-secondary))]" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            <SessionList
              title="Waiting Queue"
              sessions={waitingSessions}
              activeSessionId={currentSession?.id}
              onSelectSession={handleSelectSession}
              emptyMessage="No waiting customers"
            />
            <SessionList
              title="My Active Chats"
              sessions={activeSessions}
              activeSessionId={currentSession?.id}
              onSelectSession={handleSelectSession}
              emptyMessage="No active chats"
            />
          </div>
        </aside>

        {/* Chat area */}
        <main className="flex-1 h-full overflow-hidden">
          <ChatWindow
            session={currentSession}
            employee={employee}
            messages={messages}
            isTyping={customerTyping}
            onSend={handleSendMessage}
            onTyping={handleTyping}
            onAssign={handleAssign}
            onCloseSession={handleCloseSession}
          />
        </main>
      </div>
    </div>
  )
}
