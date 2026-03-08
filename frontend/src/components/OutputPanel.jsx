import { CodeViewer } from "./CodeViewer";

function Card({ title, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h3 className="mb-3 text-sm font-semibold text-slate-800 dark:text-slate-200">{title}</h3>
      {children}
    </section>
  );
}

export function OutputPanel({ code, explanation, pinConfiguration }) {
  const pinText = pinConfiguration?.length
    ? pinConfiguration.map((item) => `${item.signal}: ${item.pin} (${item.mode})`).join("\n")
    : "Pin configuration will appear here.";

  return (
    <div className="space-y-4">
      <Card title="Generated Firmware Code">
        <CodeViewer code={code} />
      </Card>

      <Card title="Explanation">
        <p className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">
          {explanation || "Explanation will appear here."}
        </p>
      </Card>

      <Card title="Pin Configuration">
        <pre className="whitespace-pre-wrap rounded-xl bg-slate-100 p-3 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-200">
          {pinText}
        </pre>
      </Card>
    </div>
  );
}
