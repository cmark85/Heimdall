import asyncio
import serial
import re
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

try:
    ser = serial.Serial('COM11', 115200, timeout=0.1)
    print(f"Successfully connected to {ser.name}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None


def clean_log_line(line: str):

    if not line:
        return None
        
    clean_text = ansi_escape.sub('', line)
    
    clean_text = clean_text.replace("uart:~$ ", "")
    
    clean_text = clean_text.strip()
    
    if not clean_text:
        return None
        
    return clean_text

def read_from_serial_port():
    if ser and ser.is_open:
        try:
            raw_data = ser.readline()
            if raw_data:
                text = raw_data.decode('utf-8', errors='replace')
                
                return clean_log_line(text)
                
        except Exception as e:
            print(f"Serial Read Error: {e}")
    return None


# --- Router ---
@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")

    # --- 任務 1: Reading the serial data and pushing it to the webpage ---
    async def serial_reader_task():
        try:
            while True:
                log_line = await asyncio.to_thread(read_from_serial_port)
                
                if log_line:
                    await websocket.send_text(log_line)
                else:
                    await asyncio.sleep(0.01)
                    
        except asyncio.CancelledError:
            print("Serial reader task cancelled")
        except Exception as e:
            print(f"WebSocket sending error: {e}")

    reader_task = asyncio.create_task(serial_reader_task())

    # --- Task 2:Receive user input string to serial port ---
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Web Command: {data}")
            
            await websocket.send_text(f"[SYSTEM] Sending command to PFR: {data}")

            if ser and ser.is_open:
                cmd_bytes = (data + "\n").encode('utf-8')
                await asyncio.to_thread(ser.write, cmd_bytes)

    except WebSocketDisconnect:
        print("Client disconnected")
        reader_task.cancel()
    except Exception as e:
        print(f"Error: {e}")
        reader_task.cancel()