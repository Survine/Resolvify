import { cn } from '../../utils/cn'
import { Loader2 } from 'lucide-react'

const variants = {
  primary: 'bg-[hsl(var(--brand))] text-white hover:bg-[hsl(var(--brand-hover))] shadow-sm',
  secondary: 'bg-[hsl(var(--bg-tertiary))] text-[hsl(var(--text-primary))] hover:bg-[hsl(var(--border))]',
  danger: 'bg-[hsl(var(--danger))] text-white hover:opacity-90',
  ghost: 'hover:bg-[hsl(var(--surface-hover))] text-[hsl(var(--text-secondary))]',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
}

export default function Button({
  children, variant = 'primary', size = 'md', loading, className, ...props
}) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-[var(--radius)] font-medium',
        'transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--brand))] focus-visible:ring-offset-2',
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}
