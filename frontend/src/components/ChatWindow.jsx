import MessageBubble from './MessageBubble'
import ThinkingIndicator from './ThinkingIndicator'

export default function ChatWindow({ messages, messagesEndRef, loading }) {
  // 判断是否需要显示思考中：loading 为 true，且最后一条 assistant 消息内容为空
  const showThinking = loading && (() => {
    const lastMsg = messages[messages.length - 1]
    return !lastMsg || lastMsg.role === 'user' || (lastMsg.role === 'assistant' && !lastMsg.content && !lastMsg.error)
  })()

  return (
    <section className="flex-1 overflow-y-auto bg-white" data-purpose="chat-history">
      <div className="max-w-5xl mx-auto px-6 py-6 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="flex items-center justify-center" style={{ minHeight: '60vh' }}>
            <div className="text-center">
              <div className="text-5xl mb-4">💬</div>
              <p className="text-slate-600 text-lg font-medium">开始对话</p>
              <p className="text-slate-400 text-sm mt-2">让我帮你编排和管理服务</p>
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        {showThinking && <ThinkingIndicator />}
        <div ref={messagesEndRef} />
      </div>
    </section>
  )
}
