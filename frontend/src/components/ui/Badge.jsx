import { cn } from '../../utils/cn'

const colors = {
  green: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  yellow: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  gray: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
}

export default function Badge({ children, color = 'gray', className, dot }) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
      colors[color],
      className,
    )}>
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', {
        'bg-emerald-500': color === 'green',
        'bg-amber-500': color === 'yellow',
        'bg-red-500': color === 'red',
        'bg-blue-500': color === 'blue',
        'bg-gray-500': color === 'gray',
      })} />}
      {children}
    </span>
  )
}
