export default function Sidebar({ sessions, currentSessionId, onNewSession, onSelectSession, onDeleteSession, onLogout, username }) {
  return (
    <aside className="w-72 bg-[#0f172a] text-slate-300 flex flex-col h-full border-r border-slate-800 shrink-0">
      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg border border-slate-700 transition-colors duration-200"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4v16m8-8H4" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
          </svg>
          <span className="font-medium">新建对话</span>
        </button>
      </div>

      {/* History List */}
      <nav className="flex-1 overflow-y-auto px-2 space-y-1 no-scrollbar">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">最近对话</div>
        {sessions.length === 0 ? (
          <div className="px-3 py-8 text-center text-slate-500 text-sm">暂无对话记录</div>
        ) : (
          sessions.map((session) => (
            <a
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`flex items-center gap-3 px-3 py-2 rounded-md cursor-pointer transition-colors ${
                currentSessionId === session.id
                  ? 'bg-slate-800/50 text-white'
                  : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
              }`}
            >
              <svg className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
              </svg>
              <span className="truncate text-sm">{session.name}</span>
            </a>
          ))
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {username ? username.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium text-slate-200 truncate">{username || '用户'}</p>
            <p className="text-xs text-slate-500 truncate">演示账户</p>
          </div>
          <button
            onClick={onLogout}
            className="text-slate-500 hover:text-slate-300 transition-colors"
            title="退出登录"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}
