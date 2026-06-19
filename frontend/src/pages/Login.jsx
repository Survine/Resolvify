import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { MessageSquare, Lock, User, AlertCircle } from 'lucide-react'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid username or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--bg-secondary))] p-6">
      <div className="w-full max-w-md bg-[hsl(var(--surface))] rounded-2xl border border-[hsl(var(--border))] p-8 shadow-xl space-y-6 animate-slide-up">
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="w-12 h-12 bg-blue-50 dark:bg-blue-950/30 rounded-full flex items-center justify-center text-[hsl(var(--brand))]">
            <MessageSquare className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Agent Portal</h1>
          <p className="text-sm text-[hsl(var(--text-secondary))]">Sign in to Resolvify agent dashboard</p>
        </div>

        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-[var(--radius)] flex items-start gap-2 text-sm text-[hsl(var(--danger))]">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            required
            className="pl-9"
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
            className="pl-9"
          />

          <Button type="submit" loading={loading} className="w-full py-2.5">
            Log In
          </Button>
        </form>

        <div className="text-center pt-2">
          <a href="/chat" className="text-sm text-[hsl(var(--brand))] hover:underline">
            Need customer support instead?
          </a>
        </div>
      </div>
    </div>
  )
}
