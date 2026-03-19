export default function ThinkingIndicator() {
  return (
    <div className="flex justify-start gap-3">
      <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 flex-shrink-0">
        AI
      </div>
      <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm flex items-center gap-1.5">
        <span className="thinking-dot w-2 h-2 bg-slate-400 rounded-full" style={{ animationDelay: '0ms' }} />
        <span className="thinking-dot w-2 h-2 bg-slate-400 rounded-full" style={{ animationDelay: '150ms' }} />
        <span className="thinking-dot w-2 h-2 bg-slate-400 rounded-full" style={{ animationDelay: '300ms' }} />
        <span className="text-sm text-slate-400 ml-1.5">思考中</span>
      </div>
    </div>
  )
}
