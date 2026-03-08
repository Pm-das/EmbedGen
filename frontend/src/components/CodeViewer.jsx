import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export function CodeViewer({ code }) {
  const displayCode = code?.trim() ? code : "// Generated firmware will appear here.";

  function handleCopy() {
    navigator.clipboard.writeText(displayCode);
  }

  function handleDownload() {
    const blob = new Blob([displayCode], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "firmware.c";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-lg border border-slate-600 px-3 py-1 text-xs text-slate-200 hover:bg-slate-700"
        >
          Copy
        </button>
        <button
          type="button"
          onClick={handleDownload}
          className="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-500"
        >
          Download
        </button>
      </div>

      <SyntaxHighlighter
        language="c"
        style={oneDark}
        showLineNumbers
        wrapLongLines
        customStyle={{ margin: 0, borderRadius: "0.75rem", minHeight: "280px" }}
      >
        {displayCode}
      </SyntaxHighlighter>
    </div>
  );
}
