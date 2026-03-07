import json
import os
from urllib import error, request

import typer

SUPPORTED_MCUS = ["LPC2148", "Arduino Uno", "ESP32", "PIC16F877A"]
DEFAULT_API_URL = os.getenv("EMBEDGEN_API_URL", "http://localhost:8000")

app = typer.Typer(help="EmbedGen command-line interface")


def _post_json(path: str, payload: dict[str, str], api_url: str) -> dict[str, object]:
    endpoint = f"{api_url.rstrip('/')}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _infer_mcu(prompt: str) -> str:
    lowered = prompt.lower()
    for mcu in SUPPORTED_MCUS:
        if mcu.lower() in lowered:
            return mcu
    return "ESP32"


@app.command()
def generate(
    prompt: str,
    microcontroller: str = typer.Option(None, "--microcontroller", "-m", help="Target MCU"),
    api_url: str = typer.Option(DEFAULT_API_URL, "--api-url", help="EmbedGen backend base URL"),
) -> None:
    """Generate firmware code from a natural-language prompt."""
    selected_mcu = microcontroller or _infer_mcu(prompt)

    if selected_mcu not in SUPPORTED_MCUS:
        typer.echo(f"Unsupported MCU '{selected_mcu}'. Supported: {', '.join(SUPPORTED_MCUS)}")
        raise typer.Exit(code=1) from None

    payload = {"microcontroller": selected_mcu, "task": prompt}

    try:
        data = _post_json("/generate-code", payload, api_url)
    except error.HTTPError as exc:
        typer.echo(f"Backend error: HTTP {exc.code}")
        raise typer.Exit(code=1) from None
    except error.URLError as exc:
        typer.echo(f"Connection error: {exc.reason}")
        raise typer.Exit(code=1) from None

    typer.echo(f"MCU: {data.get('microcontroller', selected_mcu)}")
    typer.echo("\nGenerated C code:\n")
    typer.echo(data.get("embedded_c_code", ""))


@app.command()
def explain(
    code: str,
    microcontroller: str = typer.Option("LPC2148", "--microcontroller", "-m", help="Target MCU"),
    api_url: str = typer.Option(DEFAULT_API_URL, "--api-url", help="EmbedGen backend base URL"),
) -> None:
    """Explain register effects from an embedded code snippet."""
    try:
        data = _post_json(
            "/explain-registers", {"microcontroller": microcontroller, "code": code}, api_url
        )
    except error.HTTPError as exc:
        typer.echo(f"Backend error: HTTP {exc.code}")
        raise typer.Exit(code=1) from None
    except error.URLError as exc:
        typer.echo(f"Connection error: {exc.reason}")
        raise typer.Exit(code=1) from None

    typer.echo(f"MCU: {data.get('microcontroller', 'Unknown')}")
    typer.echo("\nRegisters:")

    registers = data.get("registers", [])
    if not isinstance(registers, list) or not registers:
        typer.echo("- No register details returned.")
        return

    for entry in registers:
        if isinstance(entry, dict):
            typer.echo(f"- {entry.get('register', 'N/A')}: {entry.get('description', '')}")
            typer.echo(f"  Effect: {entry.get('effect', '')}")


if __name__ == "__main__":
    app()
