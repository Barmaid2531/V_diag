# V_diag

Read-only Volvo diagnostic research project, beginning with USB adapter identification.

## Milestone 1
- Detect serial/COM ports on Windows.
- Connect to a selected USB serial adapter.
- Identify an ELM-compatible interface using adapter-only AT commands.
- Save a diagnostic connection log.

This milestone does **not** query vehicle ECUs and does not clear or modify vehicle faults.

## Install
Windows 10/11, Python 3.10+, and the vLinker FS V2 USB driver.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
vdiag ports
vdiag identify --port COM3
```

The identification sequence sends only adapter AT commands: ATZ, ATE0, ATL0, ATS0, ATH1, ATI, and ATDP. No vehicle diagnostic service request is sent.

## Safety boundary
Read-only only. No DTC clearing, coding, adaptations, resets, actuator tests, or other active commands.

The vLinker FS V2 may support generic OBD-II. Full-vehicle diagnostics on the 2021 Volvo V60 SPA platform may require a different transport/interface. Test the current adapter before purchasing hardware.
