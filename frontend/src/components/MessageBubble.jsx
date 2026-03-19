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

  // 内容为空且无工具状态和错误时不渲染（由 ThinkingIndicator 接管）
  if (!message.content && !message.toolStatus && !message.error) return null

  return (
    <div className="flex justify-start gap-3">
      <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 flex-shrink-0">
        AI
      </div>
      <div className="flex flex-col gap-2">
        {message.content ? (
          <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-2xl shadow-sm">
            <p className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap break-words">{message.content}</p>
          </div>
        ) : message.toolStatus ? (
          <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-md shadow-sm">
            <p className="text-sm text-slate-500">正在调用技能...</p>
          </div>
        ) : null}
        {message.toolStatus && (
          <ToolStatus toolName={message.toolStatus} />
        )}
        {message.error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 max-w-md">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-600">{message.error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
