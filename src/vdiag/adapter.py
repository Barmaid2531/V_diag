"""Safe, adapter-only ELM-compatible serial identification."""
from dataclasses import dataclass, field
import time
from typing import Callable

import serial
from serial.tools import list_ports


@dataclass
class AdapterResult:
    port: str
    baudrate: int
    responses: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def identified(self) -> bool:
        ati = self.responses.get("ATI", "").upper()
        return bool(ati and "?" not in ati and "ERROR" not in ati)


def available_ports() -> list[dict[str, str]]:
    return [
        {
            "device": p.device,
            "description": p.description or "Unknown device",
            "hardware_id": p.hwid or "",
        }
        for p in list_ports.comports()
    ]


class ElmSerial:
    """Minimal serial transport. Vehicle diagnostic requests are blocked."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def __enter__(self):
        self._serial = serial.Serial(
            self.port, self.baudrate, timeout=self.timeout,
            write_timeout=self.timeout,
        )
        time.sleep(0.3)
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._serial and self._serial.is_open:
            self._serial.close()

    def command(self, command: str, settle: float = 0.15) -> str:
        if not command.startswith("AT"):
            raise ValueError("Safety guard: only adapter AT commands are permitted.")
        if any(ch in command for ch in "\r\n"):
            raise ValueError("Command must be a single line.")
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Serial connection is not open.")

        self._serial.reset_input_buffer()
        self._serial.write((command + "\r").encode("ascii"))
        self._serial.flush()
        time.sleep(settle)

        chunks = []
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            data = self._serial.read(self._serial.in_waiting or 1)
            if data:
                chunks.append(data)
                if b">" in data:
                    break
        return b"".join(chunks).decode("ascii", errors="replace").replace("\r", "\n").replace(">", "").strip()


def identify_adapter(port: str, baudrate: int = 115200, timeout: float = 1.5,
                     logger: Callable[[str], None] | None = None) -> AdapterResult:
    """Identify the adapter using AT commands only; never query vehicle ECUs."""
    result = AdapterResult(port=port, baudrate=baudrate)
    log = logger or (lambda _message: None)
    sequence = [
        ("ATZ", 0.8), ("ATE0", 0.15), ("ATL0", 0.15),
        ("ATS0", 0.15), ("ATH1", 0.15), ("ATI", 0.15), ("ATDP", 0.15),
    ]
    try:
        with ElmSerial(port, baudrate, timeout) as elm:
            for command, settle in sequence:
                response = elm.command(command, settle)
                result.responses[command] = response
                log(f"> {command}\n{response or '[no response]'}")
    except (serial.SerialException, OSError, RuntimeError, ValueError) as exc:
        result.errors.append(str(exc))
        log(f"ERROR: {exc}")
    return result
