const NAV_ITEMS = [
  "Firmware Generator",
  "Code Debugger",
  "Register Explainer",
  "Circuit Helper",
];

export function Sidebar({ activeItem, onSelect }) {
  return (
    <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Tools
      </h2>
      <nav className="space-y-2">
        {NAV_ITEMS.map((item) => {
          const active = activeItem === item;
          return (
            <button
              key={item}
              type="button"
              onClick={() => onSelect(item)}
              className={`w-full rounded-xl px-3 py-2 text-left text-sm font-medium transition ${
                active
                  ? "bg-blue-600 text-white"
                  : "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
              }`}
            >
              {item}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
