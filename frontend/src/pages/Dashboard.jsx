import React, { useState } from "react";

import { CodeViewer } from "../components/CodeViewer";
import { PromptForm } from "../components/PromptForm";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function Dashboard() {
  const [generatedCode, setGeneratedCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate(payload) {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/generate-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(`Request failed (${response.status}): ${details || "No details"}`);
      }

      const data = await response.json();
      setGeneratedCode(data.embedded_c_code || "// No code returned by backend.");
    } catch (requestError) {
      setError(requestError.message || "Unable to generate firmware.");
      setGeneratedCode("");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="dashboard-shell">
      <section className="dashboard-card">
        <h1>EmbedGen Dashboard</h1>
        <p className="subtext">Generate microcontroller firmware from natural language prompts.</p>

        <PromptForm onSubmit={handleGenerate} isLoading={isLoading} />

        {error && <p className="error-text">{error}</p>}

        <div className="output-block">
          <h2>Generated Firmware</h2>
          <CodeViewer code={generatedCode} />
        </div>
      </section>
    </main>
  );
}
