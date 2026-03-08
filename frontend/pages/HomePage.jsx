import React, { useMemo, useState } from "react";

import { CodeViewer } from "../components/CodeViewer";

const MCU_OPTIONS = ["LPC2148", "Arduino Uno", "ESP32", "PIC16F877A"];
const TABS = ["Code Generator", "Code Debugger", "Register Explainer"];
const API_BASE_URL = import.meta?.env?.VITE_API_BASE_URL || "http://localhost:8000";

export function HomePage() {
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [microcontroller, setMicrocontroller] = useState("ESP32");
  const [task, setTask] = useState("Read ADC value and send via UART every second");
  const [generatedCode, setGeneratedCode] = useState("");
  const [explanation, setExplanation] = useState("");
  const [pinConfiguration, setPinConfiguration] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const pinConfigText = useMemo(() => {
    if (pinConfiguration.length === 0) {
      return "";
    }

    return pinConfiguration
      .map((entry) => `${entry.signal}: ${entry.pin} (${entry.mode})`)
      .join("\n");
  }, [pinConfiguration]);

  async function handleGenerate(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/generate-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ microcontroller, task }),
      });

      if (!response.ok) {
        const bodyText = await response.text();
        throw new Error(`Backend request failed (${response.status}): ${bodyText || "no details"}`);
      }

      const data = await response.json();
      setGeneratedCode(data.embedded_c_code || "");
      setExplanation(data.explanation || "");
      setPinConfiguration(Array.isArray(data.pin_configuration) ? data.pin_configuration : []);
    } catch (requestError) {
      setError(requestError.message || "Unable to generate code.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <div className="mx-auto max-w-6xl rounded-xl bg-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold">EmbedGen Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">
          Build, debug, and explain embedded firmware behavior from natural-language prompts.
        </p>

        <div className="mt-6 flex flex-wrap gap-2 border-b border-slate-200 pb-3">
          {TABS.map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`rounded-md px-4 py-2 text-sm font-medium transition ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === "Code Generator" && (
          <section className="mt-6 grid gap-6 lg:grid-cols-2">
            <form onSubmit={handleGenerate} className="space-y-4 rounded-lg border p-4">
              <h2 className="text-lg font-semibold">Code Generator</h2>

              <label className="grid gap-2">
                <span className="text-sm font-medium">Microcontroller</span>
                <select
                  className="rounded border border-slate-300 p-2"
                  value={microcontroller}
                  onChange={(event) => setMicrocontroller(event.target.value)}
                >
                  {MCU_OPTIONS.map((mcu) => (
                    <option key={mcu} value={mcu}>
                      {mcu}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid gap-2">
                <span className="text-sm font-medium">Task Prompt</span>
                <textarea
                  className="min-h-36 rounded border border-slate-300 p-2"
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  placeholder="Describe the firmware behavior you need"
                />
              </label>

              <button
                type="submit"
                disabled={isLoading}
                className="rounded bg-blue-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {isLoading ? "Generating..." : "Generate Code"}
              </button>

              {error && <p className="text-sm text-red-600">{error}</p>}
            </form>

            <div className="space-y-4 rounded-lg border p-4">
              <h3 className="text-lg font-semibold">Generated Output</h3>

              <CodeViewer
                code={generatedCode}
                filename={`${microcontroller.toLowerCase().replace(/\s+/g, "_")}_firmware.c`}
              />

              <div>
                <p className="mb-1 text-sm font-medium">Explanation</p>
                <p className="rounded bg-slate-50 p-3 text-sm text-slate-700">
                  {explanation || "Generation explanation will appear here."}
                </p>
              </div>

              <div>
                <p className="mb-1 text-sm font-medium">Pin Configuration</p>
                <pre className="rounded bg-slate-50 p-3 text-xs text-slate-700">
                  {pinConfigText || "Pin mapping will appear here."}
                </pre>
              </div>
            </div>
          </section>
        )}

        {activeTab === "Code Debugger" && (
          <section className="mt-6 rounded-lg border p-4">
            <h2 className="text-lg font-semibold">Code Debugger</h2>
            <p className="mt-2 text-sm text-slate-600">
              Future module: upload firmware and inspect probable logic/runtime errors.
            </p>
          </section>
        )}

        {activeTab === "Register Explainer" && (
          <section className="mt-6 rounded-lg border p-4">
            <h2 className="text-lg font-semibold">Register Explainer</h2>
            <p className="mt-2 text-sm text-slate-600">
              Future module: parse register names and explain bit-fields in plain language.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
