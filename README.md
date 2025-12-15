# Project Heimdall: PFR Monitor WebUI

**Project Heimdall** is a lightweight, browser-based interface designed for monitoring Intel PFR (Platform Firmware Resilience) status. It bridges the hardware UART interface to a modern WebUI, allowing developers to view real-time logs and send shell commands directly from a web browser.

## Features 
* **Real-time Log Streaming:** View PFR boot logs and status updates instantly via WebSocket.
* **Command Injection:** Send shell commands (e.g., `status`, `reboot`) to the board.
* **Auto-scrolling Console:** Hacker-style console UI with auto-scroll support.
* **Connection Status:** Visual indicator for WebSocket/Hardware connection state.

## Prerequisites
* **OS:** Windows 10/11
* **Python:** Version 3.10 or higher (Installed with "Add to PATH" enabled)
* **Hardware:** PFR Board connected via USB-TTL Adapter

## Installation

### 1. Create a Virtual Environment

Open your terminal (CMD) in the project directory and run:

```cmd
py -m venv venv

```

### 2. Activate the Virtual Environment### 2. Activate the Virtual Environment**Fo

```cmd
venv\Scripts\activate.bat

```

**For PowerShell:**

```powershell
venv\Scripts\activate

```

*(Note: You should see `(venv)` appear at the beginning of your command line prompt.)*

### 3. Install Dependencies```cmd
py -m pip install fastapi uvicorn pyserial websockets jinja2

```

## Usage
### 1. Connect HardwareConnect your PFR Board to the PC via the USB-TTL adapter.

### 2. Start the ServerRun the following command in your terminal:

```cmd
py -m uvicorn main:app --reload

```

*Note: We use `py -m uvicorn` to ensure the system finds the correct executable within the virtual environment.*

### 3. Access the WebUI Once the server starts, you will see a message indicating Uvicorn is running

1. Open your web browser (Chrome, Edge, etc.).
2. Navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
3. You should now see the Heimdall dashboard.
*(Depending on your update: Select the COM port from the UI or check the console for auto-connection status.)*

## Troubleshooting**Error: "uvicorn is not recognized..."**

* Make sure you are using `py -m uvicorn` instead of just `uvicorn`.
* Ensure your virtual environment is activated (`(venv)` is visible).

**Error: "Access is denied" or "PermissionError" on COM Port**

* Check if another program (like Putty, TeraTerm, or a previous Python instance) is using the COM port.
* Close other terminal software or unplug/replug the USB cable.

**Error: PowerShell script execution disabled**

* If `venv\Scripts\activate` fails in PowerShell, try using Command Prompt (CMD) instead, or run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell.

