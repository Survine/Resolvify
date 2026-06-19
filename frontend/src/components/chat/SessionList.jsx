import Badge from '../ui/Badge'
import { cn } from '../../utils/cn'

export default function SessionList({ sessions, activeSessionId, onSelectSession, title, emptyMessage }) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs font-bold text-[hsl(var(--text-secondary))] uppercase tracking-wider px-1">
        {title} ({sessions.length})
      </h3>
      {sessions.length === 0 ? (
        <p className="text-sm text-[hsl(var(--text-muted))] italic py-2 px-1">{emptyMessage}</p>
      ) : (
        <div className="space-y-2">
          {sessions.map((session) => {
            const isSelected = activeSessionId === session.id
            const statusColor = session.status === 'active' ? 'blue' : session.status === 'waiting' ? 'yellow' : 'gray'

            return (
              <button
                key={session.id}
                onClick={() => onSelectSession(session)}
                className={cn(
                  'w-full text-left p-3.5 rounded-[var(--radius)] border transition-all duration-150',
                  'hover:bg-[hsl(var(--surface-hover))] hover:border-[hsl(var(--text-muted))]',
                  isSelected
                    ? 'bg-[hsl(var(--surface-hover))] border-[hsl(var(--brand))] ring-1 ring-[hsl(var(--brand))]'
                    : 'bg-[hsl(var(--surface))] border-[hsl(var(--border))]'
                )}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="font-semibold text-sm">Session #{session.id}</span>
                  <Badge color={statusColor}>{session.status}</Badge>
                </div>
                <div className="text-xs space-y-0.5 text-[hsl(var(--text-secondary))]">
                  <p className="font-medium text-[hsl(var(--text-primary))]">
                    {session.customer ? session.customer.name : 'Unknown customer'}
                  </p>
                  <p>{session.shop ? session.shop.name : 'Unknown shop'}</p>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
