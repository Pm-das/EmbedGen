import { useState } from "react";

const MCU_OPTIONS = ["LPC2148", "Arduino Uno", "ESP32", "PIC16F877A"];

export function PromptForm({ onSubmit, isLoading }) {
  const [microcontroller, setMicrocontroller] = useState("LPC2148");
  const [task, setTask] = useState(
    "Generate LPC2148 code to read ADC and send it over UART every second"
  );

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({ microcontroller, task });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
        Microcontroller
        <select
          value={microcontroller}
          onChange={(event) => setMicrocontroller(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        >
          {MCU_OPTIONS.map((mcu) => (
            <option key={mcu} value={mcu}>
              {mcu}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
        Firmware Prompt
        <textarea
          value={task}
          onChange={(event) => setTask(event.target.value)}
          rows={7}
          placeholder="Generate LPC2148 code to read ADC and send it over UART every second"
          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
      </label>

      <button
        type="submit"
        disabled={isLoading}
        className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-500"
      >
        {isLoading && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
        )}
        {isLoading ? "Generating firmware..." : "Generate Firmware"}
      </button>
    </form>
  );
}
