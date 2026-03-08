export function Header({ darkMode, onToggleDarkMode }) {
  return (
    <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-6 py-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-600 text-xl text-white">⚡</div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">EmbedGen</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">AI Firmware Generator</p>
        </div>
      </div>

      <button
        type="button"
        onClick={onToggleDarkMode}
        className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
      >
        {darkMode ? "☀️ Light" : "🌙 Dark"}
      </button>
    </header>
  );
}
