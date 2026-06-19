import { Loader2 } from 'lucide-react'

export default function Loader({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--brand))]" />
      <p className="text-sm text-[hsl(var(--text-muted))]">{text}</p>
    </div>
  )
}
