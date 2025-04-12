from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/get-m3u8")
def get_m3u8():
    # Simulated m3u8 stream URL (replace with your logic)
    return {"m3u8_url": "https://example.com/stream.m3u8"}
