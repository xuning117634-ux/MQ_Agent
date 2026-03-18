export default function ToolStatus({ toolName }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-center justify-between max-w-sm">
      <div className="flex items-center gap-3">
        <div className="relative flex h-3 w-3">
          <span className="tool-loading-pulse absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
        </div>
        <span className="text-sm font-medium text-slate-700">{toolName}</span>
      </div>
    </div>
  )
}
