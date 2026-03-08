# EmbedGen Architecture

## Overview
EmbedGen is an AI-assisted developer tool that transforms natural-language instructions into embedded firmware code and supporting hardware guidance.

## Components
- **Backend (FastAPI):** Exposes generation, circuit, and register explanation APIs.
- **Frontend (React + TailwindCSS):** Dashboard for code generation and output review.
- **CLI (Typer):** Terminal workflows that call backend APIs.
- **Knowledge Bases:** Firmware templates, circuit mappings, and register explanation JSON catalogs.

## Firmware Generation API
**Endpoint:** `POST /generate-code`

**Input payload:**
```json
{
  "microcontroller": "LPC2148",
  "task": "Read ADC value and send via UART every second"
}
```

**Response payload:**
- `embedded_c_code`: Generated embedded C template.
- `explanation`: Human-readable summary of generated behavior.
- `pin_configuration`: Pin mapping list for the selected MCU.

## Circuit Suggestion API
**Endpoint:** `POST /generate-circuit`

**Input payload:**
```json
{
  "microcontroller": "LPC2148",
  "task": "Temperature sensor using ADC"
}
```

**Response payload:**
- `required_components`: Bill of materials for the circuit.
- `pin_connections`: Pin-to-pin wiring map.
- `wiring_description`: Human-readable wiring guidance.

## Register Explanation API
**Endpoint:** `POST /explain-registers`

**Input payload:**
```json
{
  "microcontroller": "LPC2148",
  "code": "U0LCR = 0x83; U0DLL = 97;"
}
```

**Response payload:**
- `microcontroller`: Target MCU used for register lookup.
- `code`: Original input code snippet.
- `registers`: List of parsed register entries with `register`, `description`, and `effect`.

## CLI Usage
```bash
embedgen generate "UART code for LPC2148"
embedgen explain "U0LCR = 0x83; U0DLL = 97;" --microcontroller "LPC2148"
```

## Data Flow
1. User submits task/code from frontend or CLI.
2. Backend validates payload and routes to service layer.
3. Service resolves MCU templates/knowledge and returns structured JSON.
4. Client renders code, wiring suggestions, and register explanations.

## Supported MCU Families
- LPC2148
- Arduino Uno
- ESP32
- PIC16F877A


## Reliability and Validation
- Pydantic request models enforce MCU enum validation, task/code length limits, and assignment checks for register explanation snippets.
- API middleware logs request lifecycle with request ID and execution time to improve observability in production.
