from backend.services.generator import (
    explain_registers,
    generate_circuit_suggestion,
    generate_firmware_template,
)


def test_explain_registers_unknown_token_capture() -> None:
    payload = explain_registers("LPC2148", "U0LCR = 0x83; UNKNOWN_REG = 1;")
    assert any(item["register"] == "U0LCR" for item in payload["registers"])
    assert "UNKNOWN_REG" in payload["unknown_registers"]


def test_generate_firmware_fallback_peripheral() -> None:
    payload = generate_firmware_template("ESP32", "Do something custom")
    assert payload["peripheral"] == "gpio"
    assert "embedded_c_code" in payload


def test_generate_circuit_fallback() -> None:
    payload = generate_circuit_suggestion("ESP32", "Custom non-mapped task")
    assert "required_components" in payload
    assert len(payload["pin_connections"]) >= 1


def test_explain_registers_no_matches_message() -> None:
    payload = explain_registers("ESP32", "NON_EXISTENT = 1;")
    assert payload["registers"] == []
    assert "No known registers" in payload["message"]
