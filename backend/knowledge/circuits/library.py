from __future__ import annotations

CIRCUIT_LIBRARY: dict[str, dict[str, dict[str, object]]] = {
    "LPC2148": {
        "adc": {
            "required_components": [
                "LPC2148 development board",
                "LM35 temperature sensor",
                "10kΩ resistor (optional pull-down)",
                "0.1uF decoupling capacitor",
                "USB-UART adapter (for data output)",
                "Breadboard and jumper wires",
            ],
            "pin_connections": [
                {"from": "LM35 VCC", "to": "3.3V", "notes": "Sensor supply"},
                {"from": "LM35 GND", "to": "GND", "notes": "Common ground"},
                {"from": "LM35 VOUT", "to": "P0.28 / AD0.1", "notes": "ADC channel input"},
                {"from": "P0.0 / TXD0", "to": "USB-UART RX", "notes": "Optional serial telemetry"},
            ],
            "wiring_description": (
                "Power the LM35 from 3.3V and connect its output to AD0.1 (P0.28). "
                "Use shared ground between sensor, LPC2148, and USB-UART adapter. "
                "Add a 0.1uF capacitor near sensor VCC/GND for noise reduction."
            ),
        }
    },
    "Arduino Uno": {
        "adc": {
            "required_components": [
                "Arduino Uno",
                "LM35 or TMP36 temperature sensor",
                "0.1uF capacitor",
                "Breadboard and jumper wires",
            ],
            "pin_connections": [
                {"from": "Sensor VCC", "to": "5V", "notes": "Power rail"},
                {"from": "Sensor GND", "to": "GND", "notes": "Common ground"},
                {"from": "Sensor VOUT", "to": "A0", "notes": "ADC input"},
            ],
            "wiring_description": "Connect the analog sensor output to A0 and share GND. Add a local decoupling capacitor across sensor supply pins.",
        }
    },
    "ESP32": {
        "adc": {
            "required_components": [
                "ESP32 DevKit",
                "LM35/TMP36 temperature sensor",
                "Voltage divider (if sensor output can exceed 3.3V)",
                "Breadboard and jumper wires",
            ],
            "pin_connections": [
                {"from": "Sensor VCC", "to": "3.3V", "notes": "Power rail"},
                {"from": "Sensor GND", "to": "GND", "notes": "Common ground"},
                {"from": "Sensor VOUT", "to": "GPIO34 / ADC1_CH6", "notes": "ADC input-only pin"},
            ],
            "wiring_description": "Use ADC1 channel pin GPIO34 for stable readings. Ensure the analog voltage stays within 0-3.3V range.",
        }
    },
    "PIC16F877A": {
        "adc": {
            "required_components": [
                "PIC16F877A board",
                "LM35 temperature sensor",
                "20MHz crystal + capacitors (if board requires)",
                "Breadboard and jumper wires",
            ],
            "pin_connections": [
                {"from": "Sensor VCC", "to": "5V", "notes": "Power rail"},
                {"from": "Sensor GND", "to": "GND", "notes": "Common ground"},
                {"from": "Sensor VOUT", "to": "RA0 / AN0", "notes": "ADC channel 0"},
            ],
            "wiring_description": "Wire LM35 output to AN0 and configure ADCON registers for analog channel AN0 with right-justified conversion results.",
        }
    },
}


def default_circuit(mcu: str, task: str) -> dict[str, object]:
    return {
        "microcontroller": mcu,
        "task": task,
        "required_components": [
            f"{mcu} development board",
            "Target peripheral module",
            "Breadboard and jumper wires",
            "Regulated power supply",
        ],
        "pin_connections": [
            {
                "from": "Peripheral signal",
                "to": "MCU peripheral pin",
                "notes": "Select pin based on datasheet",
            },
            {"from": "Peripheral GND", "to": "MCU GND", "notes": "Common ground required"},
        ],
        "wiring_description": "Identify the peripheral in the task and map it to the MCU pin functions from datasheet before powering the circuit.",
    }
