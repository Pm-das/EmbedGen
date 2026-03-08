import { useEffect, useState } from "react";

import { Header } from "../components/Header";
import { OutputPanel } from "../components/OutputPanel";
import { PromptForm } from "../components/PromptForm";
import { Sidebar } from "../components/Sidebar";

const API_BASE_URL = "http://localhost:8000";

export function Dashboard() {
  const [activeItem, setActiveItem] = useState("Firmware Generator");
  const [darkMode, setDarkMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [output, setOutput] = useState({ code: "", explanation: "", pinConfiguration: [] });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  async function handleGenerate(payload) {
    setIsLoading(true);
    setError("");

    try {
      console.log("Sending request:", payload);
      const response = await fetch(`${API_BASE_URL}/generate-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(`Backend request failed (${response.status}): ${details || "No details"}`);
      }

      const data = await response.json();
      setOutput({
        code: data.embedded_c_code || data.code || "",
        explanation: data.explanation || "",
        pinConfiguration: data.pin_configuration || data.pins || [],
      });
    } catch (requestError) {
      setError(requestError.message || "Failed to fetch from backend.");
      setOutput({ code: "", explanation: "", pinConfiguration: [] });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto max-w-7xl space-y-4 p-4 md:p-6">
        <Header darkMode={darkMode} onToggleDarkMode={() => setDarkMode((prev) => !prev)} />

        <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
          <Sidebar activeItem={activeItem} onSelect={setActiveItem} />

          <main className="space-y-4">
            <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h2 className="mb-1 text-lg font-semibold">{activeItem}</h2>

              {activeItem === "Firmware Generator" ? (
                <>
                  <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
                    Enter a firmware requirement and generate MCU-specific starter code.
                  </p>
                  <PromptForm onSubmit={handleGenerate} isLoading={isLoading} />
                </>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {activeItem} module is ready for integration. Switch to Firmware Generator to run
                  end-to-end prompt-to-code flow.
                </p>
              )}

              {error && (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
                  {error}
                </div>
              )}
            </section>

            <OutputPanel
              code={output.code}
              explanation={output.explanation}
              pinConfiguration={output.pinConfiguration}
            />
          </main>
        </div>
      </div>
    </div>
  );
}
