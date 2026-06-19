import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import Button from '../ui/Button'
import Input from '../ui/Input'

export default function MessageInput({ onSend, onTyping, disabled }) {
  const [text, setText] = useState('')
  const typingTimeoutRef = useRef(null)

  const handleSend = (e) => {
    e.preventDefault()
    if (!text.trim() || disabled) return
    onSend(text.trim())
    setText('')
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
      onTyping(false)
    }
  }

  const handleChange = (e) => {
    setText(e.target.value)
    if (onTyping) {
      onTyping(true)
      if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
      typingTimeoutRef.current = setTimeout(() => {
        onTyping(false)
      }, 2000)
    }
  }

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
    }
  }, [])

  return (
    <form onSubmit={handleSend} className="p-4 border-t border-[hsl(var(--border))] flex gap-3 bg-[hsl(var(--surface))]">
      <Input
        value={text}
        onChange={handleChange}
        placeholder="Type a message..."
        disabled={disabled}
        className="flex-1 py-2 px-3 focus:ring-1"
      />
      <Button
        type="submit"
        disabled={disabled || !text.trim()}
        className="px-4 py-2"
        aria-label="Send message"
      >
        <Send className="w-4 h-4" />
      </Button>
    </form>
  )
}
