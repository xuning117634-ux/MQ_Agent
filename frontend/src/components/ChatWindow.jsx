import MessageBubble from './MessageBubble'

export default function ChatWindow({ messages, messagesEndRef }) {
  return (
    <section className="flex-1 overflow-y-auto px-6 py-6 space-y-4 bg-white" data-purpose="chat-history">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
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
      <div ref={messagesEndRef} />
    </section>
  )
}
