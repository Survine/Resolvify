import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import { Sun, Moon, LogOut, MessageSquare } from 'lucide-react'
import Button from './ui/Button'

export default function Navbar() {
  const { employee, logout } = useAuth()
  const { dark, toggle } = useTheme()

  return (
    <nav className="border-b border-[hsl(var(--border))] bg-[hsl(var(--surface))] px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <MessageSquare className="w-6 h-6 text-[hsl(var(--brand))]" />
        <span className="font-bold text-lg tracking-tight">Resolvify</span>
      </div>

      <div className="flex items-center gap-4">
        {employee && (
          <div className="text-right">
            <p className="text-sm font-semibold">{employee.first_name} {employee.last_name}</p>
            <p className="text-xs text-[hsl(var(--text-secondary))]">{employee.role.name}</p>
          </div>
        )}

        <Button
          variant="ghost"
          size="sm"
          onClick={toggle}
          className="p-2 rounded-full"
          aria-label="Toggle theme"
        >
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>

        {employee && (
          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="p-2 rounded-full text-[hsl(var(--danger))] hover:bg-red-50 dark:hover:bg-red-950/20"
            aria-label="Logout"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        )}
      </div>
    </nav>
  )
}
