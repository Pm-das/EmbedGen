import React from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export function CodeViewer({ code }) {
  const displayCode = code?.trim() ? code : "// Generated firmware will appear here.";

  return (
    <SyntaxHighlighter
      language="c"
      style={oneDark}
      showLineNumbers
      customStyle={{
        borderRadius: "0.75rem",
        margin: 0,
        minHeight: "260px",
        background: "#0f172a",
      }}
      wrapLongLines
    >
      {displayCode}
    </SyntaxHighlighter>
  );
}
