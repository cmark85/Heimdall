import asyncio
import serial
import serial.tools.list_ports
import re
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_log_line(line: str):
    if not line: return None
    clean_text = ansi_escape.sub('', line)
    clean_text = clean_text.replace("uart:~$ ", "").strip()
    return clean_text if clean_text else None

def read_from_serial(serial_instance):
    if serial_instance and serial_instance.is_open:
        try:
            raw_data = serial_instance.readline()
            if raw_data:
                text = raw_data.decode('utf-8', errors='replace')
                return clean_log_line(text)
        except Exception as e:
            print(f"Serial Read Error: {e}")
    return None

@app.get("/api/ports")
async def get_ports():
    """Response format: ['COM3', 'COM4', 'COM11']"""
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{port_name}")
async def websocket_endpoint(websocket: WebSocket, port_name: str):
    await websocket.accept()
    print(f"Client connecting to {port_name}...")

    ser = None
    try:
        ser = serial.Serial(port_name, 115200, timeout=0.1)
        print(f"Successfully connected to {port_name}")
        await websocket.send_text(f"[SYSTEM] Connected to {port_name}")
    except Exception as e:
        error_msg = f"[SYSTEM_ERR] Failed to open {port_name}: {str(e)}"
        print(error_msg)
        await websocket.send_text(error_msg)
        await websocket.close()
        return

    async def serial_reader_task():
        try:
            while True:
                log_line = await asyncio.to_thread(read_from_serial, ser)
                if log_line:
                    await websocket.send_text(log_line)
                else:
                    await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"WebSocket sending error: {e}")

    reader_task = asyncio.create_task(serial_reader_task())

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Web Command [{port_name}]: {data}")
            
            await websocket.send_text(f"[CMD] {data}")

            if ser and ser.is_open:
                cmd_bytes = (data + "\n").encode('utf-8')
                await asyncio.to_thread(ser.write, cmd_bytes)

    except WebSocketDisconnect:
        print(f"Client disconnected from {port_name}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reader_task.cancel()
        if ser and ser.is_open:
            print(f"Closing {port_name}...")
            ser.close()