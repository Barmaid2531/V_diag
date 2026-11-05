"""Command-line interface for V_diag."""
import argparse
import json
from pathlib import Path

from .adapter import available_ports, identify_adapter


def _ports(_args):
    ports = available_ports()
    if not ports:
        print("No serial ports detected.")
        return 1
    for port in ports:
        print(f"{port['device']}: {port['description']} [{port['hardware_id']}]")
    return 0


def _identify(args):
    log_lines = []

    def log(message):
        print(message)
        log_lines.append(message)

    print(f"Connecting to {args.port} at {args.baud} baud.")
    print("Adapter-only identification; no vehicle DTC request will be sent.\n")
    result = identify_adapter(args.port, args.baud, args.timeout, logger=log)
    output = {
        "port": result.port,
        "baudrate": result.baudrate,
        "identified": result.identified,
        "responses": result.responses,
        "errors": result.errors,
    }
    print("\nSummary:")
    print(json.dumps(output, indent=2))
    if args.log:
        Path(args.log).write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        print(f"\nLog saved to: {args.log}")
    return 0 if result.identified else 2


def main():
    parser = argparse.ArgumentParser(prog="vdiag", description="Read-only Volvo diagnostic development tool")
    sub = parser.add_subparsers(dest="action", required=True)
    ports_parser = sub.add_parser("ports", help="List available serial/COM ports")
    ports_parser.set_defaults(func=_ports)
    identify_parser = sub.add_parser("identify", help="Identify a serial adapter using AT commands only")
    identify_parser.add_argument("--port", required=True, help="Serial port, e.g. COM3")
    identify_parser.add_argument("--baud", type=int, default=115200)
    identify_parser.add_argument("--timeout", type=float, default=1.5)
    identify_parser.add_argument("--log", default="vdiag_adapter.log")
    identify_parser.set_defaults(func=_identify)
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
