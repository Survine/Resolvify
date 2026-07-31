import { useState, useRef, useEffect } from 'react'
import { Send, Smile } from 'lucide-react'

export default function MessageInput({ onSend, onTyping, disabled }) {
  const [text, setText] = useState('')
  const typingTimeoutRef = useRef(null)
  const textareaRef = useRef(null)

  const handleSend = (e) => {
    e?.preventDefault()
    if (!text.trim() || disabled) return
    onSend(text.trim())
    setText('')
    
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
      onTyping?.(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleChange = (e) => {
    setText(e.target.value)
    
    // Auto-expand textarea height up to max
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }

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
    <form
      onSubmit={handleSend}
      className="p-3 sm:p-4 border-t border-[hsl(var(--border))] bg-[hsl(var(--surface))] flex items-end gap-2.5 shadow-lg shrink-0"
    >
      <div className="relative flex-1 flex items-center bg-[hsl(var(--bg-secondary))] border border-[hsl(var(--border))] rounded-2xl focus-within:border-[hsl(var(--brand))] focus-within:ring-2 focus-within:ring-[hsl(var(--brand))/20] transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Connecting to live agent...' : 'Type a message... (Enter to send)'}
          disabled={disabled}
          className="w-full py-2.5 px-4 bg-transparent text-sm text-[hsl(var(--text-primary))] placeholder:text-[hsl(var(--text-muted))] focus:outline-none resize-none max-h-32 min-h-[42px] leading-relaxed"
        />
      </div>

      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200 shrink-0 transform active:scale-95 cursor-pointer"
        aria-label="Send message"
      >
        <Send className="w-4 h-4 ml-0.5" />
      </button>
    </form>
  )
}
