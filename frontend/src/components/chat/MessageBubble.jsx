import { cn } from '../../utils/cn'
import { formatTime } from '../../utils/formatters'
import { User, Bot, Headset } from 'lucide-react'

export default function MessageBubble({ message, isSelf }) {
  const isSystem = message.employee?.first_name === 'System' || message.isSystem

  if (isSystem) {
    return (
      <div className="flex justify-center my-2 animate-fade-in">
        <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-[hsl(var(--bg-tertiary))] text-[hsl(var(--text-secondary))] border border-[hsl(var(--border))] shadow-xs flex items-center gap-1.5">
          <Bot className="w-3.5 h-3.5 text-[hsl(var(--brand))]" />
          {message.message}
        </span>
      </div>
    )
  }

  const senderName = isSelf
    ? 'You'
    : message.employee
    ? `${message.employee.first_name} ${message.employee.last_name}`.trim()
    : 'Support Agent'

  return (
    <div
      className={cn(
        'flex gap-2.5 max-w-[85%] sm:max-w-[75%] animate-fade-in group',
        isSelf ? 'self-end flex-row-reverse' : 'self-start flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 shadow-sm',
          isSelf
            ? 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white'
            : 'bg-gradient-to-tr from-emerald-500 to-teal-600 text-white'
        )}
      >
        {isSelf ? <User className="w-4 h-4" /> : <Headset className="w-4 h-4" />}
      </div>

      {/* Message content */}
      <div className={cn('flex flex-col', isSelf ? 'items-end' : 'items-start')}>
        <span className="text-[11px] text-[hsl(var(--text-muted))] mb-1 font-medium px-1">
          {senderName}
        </span>
        <div
          className={cn(
            'px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-all duration-200',
            isSelf
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-xs shadow-blue-500/10'
              : 'bg-[hsl(var(--surface))] text-[hsl(var(--text-primary))] border border-[hsl(var(--border))] rounded-tl-xs shadow-xs hover:border-[hsl(var(--brand))/30]'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.message}</p>
          <span
            className={cn(
              'block text-[10px] mt-1.5 font-medium tracking-tight opacity-80',
              isSelf ? 'text-blue-100 text-right' : 'text-[hsl(var(--text-muted))] text-left'
            )}
          >
            {formatTime(message.created_at)}
          </span>
        </div>
      </div>
    </div>
  )
}
