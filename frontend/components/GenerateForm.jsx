import React from "react";

const MCU_OPTIONS = ["LPC2148", "Arduino", "ESP32", "PIC16F877A"];

export function GenerateForm() {
  return (
    <form className="mt-6 grid gap-4 rounded-xl bg-white p-6 shadow">
      <label className="grid gap-2">
        <span className="text-sm font-medium">MCU Target</span>
        <select className="rounded border p-2" defaultValue="ESP32">
          {MCU_OPTIONS.map((mcu) => (
            <option key={mcu} value={mcu}>
              {mcu}
            </option>
          ))}
        </select>
      </label>

      <label className="grid gap-2">
        <span className="text-sm font-medium">Instruction</span>
        <textarea
          className="min-h-28 rounded border p-2"
          placeholder="Generate UART driver with 9600 baud and RX interrupt support"
        />
      </label>

      <button type="button" className="rounded bg-blue-600 px-4 py-2 text-white">
        Generate Firmware
      </button>
    </form>
  );
}
