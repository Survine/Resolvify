import { forwardRef } from 'react'
import { cn } from '../../utils/cn'

const Input = forwardRef(({ label, error, className, ...props }, ref) => (
  <div className="space-y-1.5">
    {label && (
      <label className="block text-sm font-medium text-[hsl(var(--text-secondary))]">
        {label}
      </label>
    )}
    <input
      ref={ref}
      className={cn(
        'w-full px-3.5 py-2.5 rounded-[var(--radius)] border border-[hsl(var(--border))]',
        'bg-[hsl(var(--surface))] text-[hsl(var(--text-primary))]',
        'placeholder:text-[hsl(var(--text-muted))]',
        'focus:outline-none focus:ring-2 focus:ring-[hsl(var(--brand))] focus:border-transparent',
        'transition-all duration-150 text-sm',
        error && 'border-[hsl(var(--danger))] focus:ring-[hsl(var(--danger))]',
        className,
      )}
      {...props}
    />
    {error && <p className="text-xs text-[hsl(var(--danger))]">{error}</p>}
  </div>
))

Input.displayName = 'Input'
export default Input
