import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# When running on Render, it automatically sets the PORT environment variable.
# FastAPI will bind to this port.
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if no port is set
    uvicorn.run(app, host="0.0.0.0", port=port)
