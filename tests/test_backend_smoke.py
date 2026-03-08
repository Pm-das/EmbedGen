import pytest

try:
    from fastapi.testclient import TestClient

    from backend.main import app
except ModuleNotFoundError:  # pragma: no cover - optional dependency in constrained env
    TestClient = None
    app = None

pytestmark = pytest.mark.skipif(TestClient is None, reason="fastapi is not installed")

client = TestClient(app) if TestClient and app else None


@pytest.mark.parametrize(
    "microcontroller,task,expected_token",
    [
        ("LPC2148", "Generate UART firmware", "U0LCR"),
        ("LPC2148", "Create ADC reader", "AD0CR"),
        ("LPC2148", "Need PWM output", "PWMMR0"),
        ("LPC2148", "Use GPIO blink", "IODIR0"),
        ("LPC2148", "Implement SPI transfer", "S0SPDR"),
        ("LPC2148", "Implement I2C master", "I2C0SCLH"),
        ("LPC2148", "Add Timers periodic task", "T0MR0"),
        ("Arduino Uno", "UART output", "UCSR0B"),
        ("Arduino Uno", "Read ADC value", "ADCSRA"),
        ("Arduino Uno", "PWM control", "TCCR1A"),
        ("Arduino Uno", "GPIO blink", "DDRB"),
        ("Arduino Uno", "SPI master", "SPCR"),
        ("Arduino Uno", "I2C twi", "TWBR"),
        ("Arduino Uno", "Timers tick", "TCCR0A"),
        ("ESP32", "UART logging", "uart_param_config"),
        ("ESP32", "ADC sample", "adc1_get_raw"),
        ("ESP32", "PWM waveform", "ledc_timer_config"),
        ("ESP32", "GPIO toggle", "gpio_set_level"),
        ("ESP32", "SPI driver", "spi_bus_initialize"),
        ("ESP32", "I2C driver", "i2c_param_config"),
        ("ESP32", "Timers callback", "gptimer_new_timer"),
        ("PIC16F877A", "UART tx", "SPBRG"),
        ("PIC16F877A", "ADC conversion", "ADCON0"),
        ("PIC16F877A", "PWM output", "CCP1CON"),
        ("PIC16F877A", "GPIO pin", "TRISB0"),
        ("PIC16F877A", "SPI mssp", "SSPCON"),
        ("PIC16F877A", "I2C mssp", "SSPADD"),
        ("PIC16F877A", "Timers periodic", "T1CON"),
    ],
)
def test_generate_code_template_selection(
    microcontroller: str, task: str, expected_token: str
) -> None:
    response = client.post(
        "/generate-code",
        json={"microcontroller": microcontroller, "task": task},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["microcontroller"] == microcontroller
    assert expected_token in payload["embedded_c_code"]
    assert payload["peripheral"] in payload["supported_peripherals"]
    assert len(payload["pin_configuration"]) >= 1


def test_generate_circuit_endpoint() -> None:
    response = client.post(
        "/generate-circuit",
        json={"microcontroller": "LPC2148", "task": "Temperature sensor using ADC"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["microcontroller"] == "LPC2148"
    assert payload["peripheral"] == "adc"
    assert len(payload["required_components"]) > 0
    assert len(payload["pin_connections"]) > 0


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_explain_registers_endpoint() -> None:
    response = client.post(
        "/explain-registers",
        json={"microcontroller": "LPC2148", "code": "U0LCR = 0x83; U0DLL = 97;"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["microcontroller"] == "LPC2148"
    assert any(item["register"] == "U0LCR" for item in payload["registers"])
    assert any(item["register"] == "U0DLL" for item in payload["registers"])
    assert all("description" in item and "effect" in item for item in payload["registers"])


def test_generate_code_validation_error_for_unknown_mcu() -> None:
    response = client.post(
        "/generate-code",
        json={"microcontroller": "STM32", "task": "UART init"},
    )
    assert response.status_code == 422


def test_explain_registers_validation_requires_assignment() -> None:
    response = client.post(
        "/explain-registers",
        json={"microcontroller": "LPC2148", "code": "U0LCR"},
    )
    assert response.status_code == 422


def test_cors_preflight_generate_code() -> None:
    response = client.options(
        "/generate-code",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
