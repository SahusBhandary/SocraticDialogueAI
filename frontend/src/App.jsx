import { useState, useRef, useEffect } from 'react'
import './App.css'

const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

const INITIAL_MESSAGE = {
  role: 'assistant',
  content: 'Hi! I am your Socratic tutor. What questions do you have?'
}

function generateSessionId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2)
}

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    let id = localStorage.getItem('sessionId')
    if (!id) {
      id = generateSessionId()
      localStorage.setItem('sessionId', id)
    }
    setSessionId(id)

    fetch(`${apiUrl}/history/${id}`)
      .then(res => res.json())
      .then(data => {
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages)
        } else {
          setMessages([INITIAL_MESSAGE])
        }
      })
      .catch(() => setMessages([INITIAL_MESSAGE]))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const autoResize = () => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'
  }

  const sendMessage = async () => {
    if (!input.trim() || loading || !sessionId) return

    const userText = input.trim()
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setMessages(prev => [...prev, { role: 'user', content: userText }])
    setLoading(true)

    try {
      const res = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, session_id: sessionId }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Please check if the server is running before continuing!'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <div className="bg-orbs">
        <div className="orb orb-moon" />
        <div className="orb orb-ember" />
        <div className="orb orb-pink" />
        <div className="orb orb-violet" />
        <div className="orb orb-green" />
      </div>

      <div className="chat-container">
        <header className="chat-header">
          <div className="moon-orb" />
          <h1 className="title">Socratic Tutor</h1>
        </header>

        <div className="messages-panel">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="avatar">{msg.role === 'assistant' ? '🌙' : '✦'}</div>
              <div className="bubble">
                <p>{msg.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="avatar">🌙</div>
              <div className="bubble loading-bubble">
                <span /><span /><span />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            ref={textareaRef}
            className="input-field"
            value={input}
            onChange={e => { setInput(e.target.value); autoResize() }}
            onKeyDown={handleKeyDown}
            placeholder="Enter any question..."
            rows={1}
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            aria-label="Send"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
