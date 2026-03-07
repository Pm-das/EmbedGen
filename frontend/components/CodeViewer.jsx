import React, { useMemo, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export function CodeViewer({ code, filename = "generated_firmware.c" }) {
  const [copied, setCopied] = useState(false);

  const safeCode = useMemo(() => {
    if (!code || code.trim().length === 0) {
      return "// Generated code will appear here.";
    }
    return code;
  }, [code]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(safeCode);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch (_error) {
      setCopied(false);
    }
  }

  function handleDownload() {
    const blob = new Blob([safeCode], { type: "text/x-c" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-medium text-slate-200">Embedded C Code</p>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="rounded bg-slate-700 px-3 py-1 text-xs text-slate-100 hover:bg-slate-600"
          >
            {copied ? "Copied" : "Copy"}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="rounded bg-blue-600 px-3 py-1 text-xs text-white hover:bg-blue-500"
          >
            Download
          </button>
        </div>
      </div>

      <SyntaxHighlighter
        language="c"
        style={oneDark}
        showLineNumbers
        customStyle={{
          margin: 0,
          borderRadius: "0.5rem",
          maxHeight: "20rem",
          fontSize: "0.75rem",
          background: "#0f172a",
        }}
        wrapLongLines
      >
        {safeCode}
      </SyntaxHighlighter>
    </div>
  );
}
