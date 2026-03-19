import ToolStatus from './ToolStatus'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-2xl shadow-md">
          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>
    )
  }

  // 内容为空时不渲染（由 ThinkingIndicator 接管）
  if (!message.content && !message.toolStatus) return null

  return (
    <div className="flex justify-start gap-3">
      <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 flex-shrink-0">
        AI
      </div>
      <div className="flex flex-col gap-2">
        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-2xl shadow-sm">
          <p className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        {message.toolStatus && (
          <ToolStatus toolName={message.toolStatus} />
        )}
      </div>
    </div>
  )
}
