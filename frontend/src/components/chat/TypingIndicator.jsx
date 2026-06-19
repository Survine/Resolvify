import { cn } from '../../utils/cn'

export default function TypingIndicator({ name, className }) {
  return (
    <div className={cn('flex items-center gap-2 text-xs text-[hsl(var(--text-secondary))] py-2 px-4 italic animate-fade-in', className)}>
      <span>{name} is typing</span>
      <div className="flex gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--text-muted))] animate-[pulse-dot_1.4s_infinite_ease-in-out]" />
        <span className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--text-muted))] animate-[pulse-dot_1.4s_infinite_ease-in-out_0.2s]" />
        <span className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--text-muted))] animate-[pulse-dot_1.4s_infinite_ease-in-out_0.4s]" />
      </div>
    </div>
  )
}
