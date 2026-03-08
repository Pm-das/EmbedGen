import React, { useState } from "react";

const MCU_OPTIONS = ["LPC2148", "Arduino Uno", "ESP32", "PIC16F877A"];

export function PromptForm({ onSubmit, isLoading }) {
  const [microcontroller, setMicrocontroller] = useState("ESP32");
  const [task, setTask] = useState("Read ADC value and send via UART every second");

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({ microcontroller, task });
  }

  return (
    <form className="prompt-form" onSubmit={handleSubmit}>
      <label>
        Microcontroller
        <select value={microcontroller} onChange={(event) => setMicrocontroller(event.target.value)}>
          {MCU_OPTIONS.map((mcu) => (
            <option key={mcu} value={mcu}>
              {mcu}
            </option>
          ))}
        </select>
      </label>

      <label>
        Firmware Prompt
        <textarea
          value={task}
          onChange={(event) => setTask(event.target.value)}
          placeholder="Describe the firmware behavior you need"
          rows={6}
        />
      </label>

      <button type="submit" disabled={isLoading}>
        {isLoading ? "Generating..." : "Generate Firmware"}
      </button>
    </form>
  );
}
