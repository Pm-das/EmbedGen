from __future__ import annotations

import json
import re
from pathlib import Path

from backend.knowledge.circuits.library import CIRCUIT_LIBRARY, default_circuit
from backend.templates.firmware_templates import (
    SUPPORTED_MCUS,
    SUPPORTED_PERIPHERALS,
    detect_peripheral,
    get_pin_configuration,
    get_template,
    normalize_mcu,
)

REGISTER_DB_FILES = {
    "LPC2148": "lpc2148_registers.json",
    "Arduino Uno": "arduino_registers.json",
    "PIC16F877A": "pic16f877a_registers.json",
}
REGISTER_TOKEN_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def generate_firmware_template(microcontroller: str, task: str) -> dict[str, object]:
    """Generate firmware template based on microcontroller + requested peripheral."""
    normalized_mcu = normalize_mcu(microcontroller)
    if normalized_mcu not in SUPPORTED_MCUS:
        normalized_mcu = "ESP32"

    peripheral = detect_peripheral(task) or "gpio"

    code = get_template(normalized_mcu, peripheral)
    pin_configuration = get_pin_configuration(normalized_mcu, peripheral)

    explanation = (
        f"Selected {normalized_mcu} {peripheral.upper()} template based on request. "
        "The code includes register/peripheral initialization, helper functions, and a runnable main loop."
    )

    return {
        "microcontroller": normalized_mcu,
        "peripheral": peripheral,
        "task": task,
        "embedded_c_code": code,
        "explanation": explanation,
        "pin_configuration": pin_configuration,
        "supported_peripherals": list(SUPPORTED_PERIPHERALS),
    }


def generate_circuit_suggestion(microcontroller: str, task: str) -> dict[str, object]:
    """Generate structured circuit suggestion JSON using circuit knowledge base."""
    normalized_mcu = normalize_mcu(microcontroller)
    if normalized_mcu not in SUPPORTED_MCUS:
        normalized_mcu = "ESP32"

    peripheral = detect_peripheral(task)
    if peripheral is None and "temperature" in task.lower():
        peripheral = "adc"

    circuit = CIRCUIT_LIBRARY.get(normalized_mcu, {}).get(peripheral or "")
    if circuit is None:
        return default_circuit(normalized_mcu, task)

    return {
        "microcontroller": normalized_mcu,
        "task": task,
        "peripheral": peripheral,
        "required_components": circuit["required_components"],
        "pin_connections": circuit["pin_connections"],
        "wiring_description": circuit["wiring_description"],
    }


def explain_registers(microcontroller: str, code: str) -> dict[str, object]:
    """Parse source code, identify register tokens, and return register explanations."""
    normalized_mcu = normalize_mcu(microcontroller)
    register_db = _load_register_database(normalized_mcu)

    parsed_tokens = REGISTER_TOKEN_PATTERN.findall(code)
    identified = _extract_registers_from_code(parsed_tokens, register_db)
    unknown_registers = sorted(
        {token for token in parsed_tokens if token.isupper() and token not in register_db}
    )

    explanations = [
        {
            "register": register_name,
            "description": register_db[register_name]["description"],
            "effect": register_db[register_name]["effect"],
        }
        for register_name in identified
    ]

    return {
        "microcontroller": normalized_mcu,
        "code": code,
        "registers": explanations,
        "unknown_registers": unknown_registers,
        "message": _explain_message(normalized_mcu, explanations),
    }


def _load_register_database(mcu: str) -> dict[str, dict[str, str]]:
    filename = REGISTER_DB_FILES.get(mcu)
    if filename is None:
        return {}

    base_dir = Path(__file__).resolve().parents[1] / "knowledge" / "registers"
    try:
        with (base_dir / filename).open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}


def _extract_registers_from_code(
    tokens: list[str], register_db: dict[str, dict[str, str]]
) -> list[str]:
    if not register_db:
        return []

    seen: set[str] = set()
    found: list[str] = []

    for token in tokens:
        if token in register_db and token not in seen:
            seen.add(token)
            found.append(token)

    return found


def _explain_message(mcu: str, explanations: list[dict[str, str]]) -> str:
    if not explanations:
        return (
            f"No known registers were identified for {mcu}. "
            "Check the code snippet and MCU name or extend the register knowledge base."
        )
    return f"Identified {len(explanations)} register(s) for {mcu}."
