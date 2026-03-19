import { useState, useRef, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import InputBar from './components/InputBar'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import LoginPage from './pages/LoginPage'
import './App.css'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const messagesEndRef = useRef(null)
  const messageBufferRef = useRef([])
  const bufferTimerRef = useRef(null)

  // Initialize from localStorage
  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUsername = localStorage.getItem('username')
    if (token && savedUsername) {
      setIsLoggedIn(true)
      setUsername(savedUsername)
      loadSessions()
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/sessions')
      if (response.ok) {
        const data = await response.json()
        const sessionList = data.sessions || []
        setSessions(sessionList)
        if (sessionList.length > 0) {
          // 选中第一个会话，从后端拉取消息
          setCurrentSessionId(sessionList[0].id)
          const detailRes = await fetch(`/api/sessions/${sessionList[0].id}`)
          if (detailRes.ok) {
            const detail = await detailRes.json()
            setMessages(detail.messages || [])
          }
        } else {
          createNewSession()
        }
      }
    } catch (err) {
      console.error('Failed to load sessions:', err)
      createNewSession()
    }
  }

  const createNewSession = async () => {
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `对话 ${new Date().toLocaleTimeString()}` })
      })
      if (response.ok) {
        const data = await response.json()
        const newSession = { id: data.id, name: data.name, createdAt: new Date(), messages: [] }
        setSessions(prev => [newSession, ...prev])
        setCurrentSessionId(data.id)
        setMessages([])
      }
    } catch (err) {
      console.error('Failed to create session:', err)
    }
  }

  const selectSession = async (sessionId) => {
    setCurrentSessionId(sessionId)
    try {
      const response = await fetch(`/api/sessions/${sessionId}`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      }
    } catch (err) {
      console.error('Failed to load session:', err)
      setMessages([])
    }
  }

  const deleteSession = async (sessionId) => {
    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (currentSessionId === sessionId) {
        if (sessions.length > 1) {
          const nextSession = sessions.find(s => s.id !== sessionId)
          selectSession(nextSession.id)
        } else {
          createNewSession()
        }
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }

  // Flush message buffer
  const flushMessageBuffer = () => {
    if (messageBufferRef.current.length > 0) {
      setMessages(prev => {
        const updated = [...prev]
        const lastMsg = updated[updated.length - 1]
        if (lastMsg && lastMsg.role === 'assistant') {
          lastMsg.content += messageBufferRef.current.join('')
        }
        return updated
      })
      messageBufferRef.current = []
    }
  }

  const handleSendMessage = async (text) => {
    if (!text.trim()) return

    // Add user message immediately
    const userMessage = { role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: currentSessionId
        })
      })

      if (!response.ok) throw new Error('API error')

      // Create assistant message object
      let assistantMessage = { role: 'assistant', content: '', toolStatus: null }

      // Add empty assistant message to messages
      setMessages(prev => [...prev, assistantMessage])

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        // Keep the last incomplete line in buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'text') {
                // Buffer text updates for batch processing
                messageBufferRef.current.push(data.content)
                assistantMessage.content += data.content

                // Clear existing timer and set new one
                if (bufferTimerRef.current) {
                  clearTimeout(bufferTimerRef.current)
                }

                // Batch update every 50ms
                bufferTimerRef.current = setTimeout(() => {
                  flushMessageBuffer()
                }, 50)
              } else if (data.type === 'tool_start') {
                flushMessageBuffer()
                assistantMessage.toolStatus = data.tool_name
                setMessages(prev => {
                  const updated = [...prev]
                  updated[updated.length - 1] = { ...assistantMessage }
                  return updated
                })
              } else if (data.type === 'tool_end') {
                flushMessageBuffer()
                assistantMessage.toolStatus = null
                setMessages(prev => {
                  const updated = [...prev]
                  updated[updated.length - 1] = { ...assistantMessage }
                  return updated
                })
              } else if (data.type === 'error') {
                flushMessageBuffer()
                assistantMessage.error = data.message || '服务异常，请稍后重试'
                assistantMessage.toolStatus = null
                setMessages(prev => {
                  const updated = [...prev]
                  updated[updated.length - 1] = { ...assistantMessage }
                  return updated
                })
              } else if (data.type === 'session_update') {
                // 更新左侧会话标题
                setSessions(prev => prev.map(s =>
                  s.id === data.session_id ? { ...s, name: data.name } : s
                ))
              }
            } catch (e) {
              // ignore parse errors
            }
          }
        }
      }

      // Final flush
      flushMessageBuffer()
    } catch (error) {
      console.error('Chat error:', error)
      // 更新已有的 assistant 消息，而不是新增
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = { ...last, error: '网络连接失败，请检查服务是否正常运行', toolStatus: null }
        } else {
          updated.push({ role: 'assistant', content: '', error: '网络连接失败，请检查服务是否正常运行' })
        }
        return updated
      })
    } finally {
      // 兜底：如果流结束但 assistant 消息既没内容也没错误，显示异常提示
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last && last.role === 'assistant' && !last.content && !last.error) {
          updated[updated.length - 1] = { ...last, error: '响应异常，请重试', toolStatus: null }
        }
        return updated
      })
      setLoading(false)
      if (bufferTimerRef.current) {
        clearTimeout(bufferTimerRef.current)
      }
    }
  }

  const handleLogin = (user) => {
    setUsername(user)
    setIsLoggedIn(true)
    loadSessions()
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setIsLoggedIn(false)
    setUsername('')
    setMessages([])
    setSessions([])
    setCurrentSessionId(null)
  }

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <style>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .tool-loading-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: .5; }
        }
        @keyframes thinking-bounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40% { transform: scale(1); opacity: 1; }
        }
        .thinking-dot {
          animation: thinking-bounce 1.4s infinite ease-in-out both;
        }
      `}</style>
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewSession={createNewSession}
        onSelectSession={selectSession}
        onDeleteSession={deleteSession}
        onLogout={handleLogout}
        username={username}
      />
      <main className="flex-1 flex flex-col relative bg-white">
        <Header />
        <ChatWindow messages={messages} messagesEndRef={messagesEndRef} loading={loading} />
        <InputBar onSendMessage={handleSendMessage} disabled={loading} />
      </main>
    </div>
  )
}

export default App
