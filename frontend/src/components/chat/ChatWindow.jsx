import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import TypingIndicator from './TypingIndicator'
import Button from '../ui/Button'
import Badge from '../ui/Badge'
import { MessageSquare, UserCheck, XCircle } from 'lucide-react'

export default function ChatWindow({
  session,
  employee,
  messages,
  isTyping,
  onSend,
  onTyping,
  onAssign,
  onCloseSession,
}) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  if (!session) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[hsl(var(--bg-secondary))] text-[hsl(var(--text-muted))] p-8">
        <MessageSquare className="w-12 h-12 mb-4 opacity-40 text-[hsl(var(--brand))]" />
        <h3 className="font-semibold text-lg text-[hsl(var(--text-primary))] mb-1">No Active Chat</h3>
        <p className="text-sm max-w-sm text-center">Select a chat session from the list on the left to start responding to customers.</p>
      </div>
    )
  }

  const isAssignedToMe = session.employee_id === employee?.id
  const canChat = session.status === 'active' && isAssignedToMe

  return (
    <div className="flex-1 flex flex-col h-full bg-[hsl(var(--bg-secondary))]">
      {/* Header */}
      <div className="p-4 border-b border-[hsl(var(--border))] bg-[hsl(var(--surface))] flex items-center justify-between shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="font-semibold text-base">Session #{session.id}</h2>
            <Badge color={session.status === 'active' ? 'blue' : 'yellow'}>{session.status}</Badge>
          </div>
          <p className="text-xs text-[hsl(var(--text-secondary))]">
            Customer: <span className="font-medium text-[hsl(var(--text-primary))]">{session.customer?.name}</span> ({session.customer?.email}) | Shop: {session.shop?.name}
          </p>
        </div>

        <div className="flex gap-2">
          {session.status === 'waiting' && (
            <Button size="sm" onClick={() => onAssign(session.id)} className="flex items-center gap-1.5">
              <UserCheck className="w-4 h-4" /> Take Session
            </Button>
          )}
          {session.status === 'active' && isAssignedToMe && (
            <Button size="sm" variant="danger" onClick={() => onCloseSession(session.id)} className="flex items-center gap-1.5">
              <XCircle className="w-4 h-4" /> Close Session
            </Button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div ref={containerRef} className="flex-1 overflow-y-auto p-4 space-y-4 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-sm text-[hsl(var(--text-muted))]">
            No messages in this chat session yet.
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id || msg.timestamp}
              message={msg}
              isSelf={!msg.is_from_customer}
            />
          ))
        )}
        {isTyping && <TypingIndicator name={session.customer?.name || 'Customer'} className="self-start" />}
      </div>

      {/* Footer message input */}
      <MessageInput
        onSend={onSend}
        onTyping={onTyping}
        disabled={!canChat}
      />
    </div>
  )
}
