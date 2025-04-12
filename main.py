from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os

app = FastAPI()

# Define input model for TV and Movie details
class MediaDetails(BaseModel):
    mode: str
    show_id: str = None
    season: str = None
    episode: str = None
    movie_id: str = None

@app.post("/get_m3u8/")
async def get_m3u8(details: MediaDetails):
    try:
        # Prepare the URL based on mode (TV or Movie)
        if details.mode == "tv":
            if not details.show_id or not details.season or not details.episode:
                raise HTTPException(status_code=400, detail="Missing TV show parameters")
            url = f"https://player.videasy.net/tv/{details.show_id}/{details.season}/{details.episode}"
        elif details.mode == "movie":
            if not details.movie_id:
                raise HTTPException(status_code=400, detail="Missing movie ID")
            url = f"https://player.videasy.net/movie/{details.movie_id}"
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use 'tv' or 'movie'.")

        # Set up browser with devtools enabled
        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.add_argument("--mute-audio")
        options.add_argument("--headless=new")  # Run in headless mode
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        time.sleep(5)  # Wait for player to fully load

        # Click play button if present
        try:
            button = driver.find_element(By.XPATH, "//button//*[name()='path' and contains(@d, 'M1.33398 8.00378')]")
            ActionChains(driver).move_to_element(button).click().perform()
        except:
            pass  # If button is not found or already playing, continue

        # Continuously check for m3u8 stream URL
        found = False
        m3u8_url = None
        while not found:
            time.sleep(5)  # Give time for m3u8 to load

            logs = driver.get_log("performance")
            for entry in logs:
                try:
                    message = json.loads(entry["message"])["message"]
                    if message["method"] == "Network.responseReceived":
                        m3u8_url = message["params"]["response"]["url"]
                        if ".m3u8" in m3u8_url:
                            found = True
                            break
                except:
                    continue

        driver.quit()

        if m3u8_url:
            return {"m3u8_url": m3u8_url}
        else:
            raise HTTPException(status_code=500, detail="M3U8 URL not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the app and bind it to the correct port (use PORT environment variable on Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Default to port 8000 if not provided
    uvicorn.run(app, host="0.0.0.0", port=port)
