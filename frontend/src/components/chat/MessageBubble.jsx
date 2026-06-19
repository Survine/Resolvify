import { cn } from '../../utils/cn'
import { formatTime } from '../../utils/formatters'

export default function MessageBubble({ message, isSelf }) {
  return (
    <div className={cn('flex flex-col max-w-[70%] animate-fade-in', isSelf ? 'self-end items-end' : 'self-start items-start')}>
      {!isSelf && (
        <span className="text-xs text-[hsl(var(--text-secondary))] mb-1 font-medium">
          {message.employee ? `${message.employee.first_name} ${message.employee.last_name}` : 'Customer'}
        </span>
      )}
      <div className={cn(
        'px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm',
        isSelf 
          ? 'bg-[hsl(var(--brand))] text-white rounded-tr-none' 
          : 'bg-[hsl(var(--surface))] text-[hsl(var(--text-primary))] border border-[hsl(var(--border))] rounded-tl-none'
      )}>
        <p className="whitespace-pre-wrap break-words">{message.message}</p>
        <span className={cn(
          'block text-[10px] mt-1 text-right',
          isSelf ? 'text-blue-100' : 'text-[hsl(var(--text-muted))]'
        )}>
          {formatTime(message.created_at)}
        </span>
      </div>
    </div>
  )
}
