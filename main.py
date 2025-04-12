from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, json
from webdriver_manager.chrome import ChromeDriverManager
import os

app = FastAPI()

class MediaRequest(BaseModel):
    mode: str
    show_id: str = None  # Required for TV mode
    season: str = None   # Required for TV mode
    episode: str = None  # Required for TV mode
    movie_id: str = None # Required for Movie mode

@app.post("/get-m3u8/")
async def get_m3u8(data: MediaRequest):
    try:
        # Handle TV Mode
        if data.mode == "tv":
            if not data.show_id or not data.season or not data.episode:
                raise HTTPException(status_code=400, detail="Missing TV Show details.")
            url = f"https://player.videasy.net/tv/{data.show_id}/{data.season}/{data.episode}"

        # Handle Movie Mode
        elif data.mode == "movie":
            if not data.movie_id:
                raise HTTPException(status_code=400, detail="Missing Movie ID.")
            url = f"https://player.videasy.net/movie/{data.movie_id}"
        
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Choose 'tv' or 'movie'.")

        # Set up browser with devtools enabled using WebDriver Manager to handle chromedriver
        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.add_argument("--mute-audio")
        options.add_argument("--headless")  # Run headless (no browser UI)

        # Initialize the Chrome WebDriver with WebDriver Manager
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Load the URL
        driver.get(url)
        time.sleep(5)  # wait for player to fully load

        # Click play button (if present)
        try:
            button = driver.find_element(By.XPATH, "//button//*[name()='path' and contains(@d, 'M1.33398 8.00378')]")
            ActionChains(driver).move_to_element(button).click().perform()
        except:
            pass  # Button not found or already clicked

        # Check for m3u8 URL
        found = False
        while not found:
            time.sleep(5)  # give time for m3u8 to load
            
            # Look for .m3u8 in the performance logs
            logs = driver.get_log("performance")
            for entry in logs:
                try:
                    message = json.loads(entry["message"])["message"]
                    if message["method"] == "Network.responseReceived":
                        url = message["params"]["response"]["url"]
                        if ".m3u8" in url:
                            found = True
                            driver.quit()
                            return {"m3u8_url": url}
                except:
                    continue

        # Quit the driver after finding the URL
        driver.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch m3u8 URL: {str(e)}")

    return {"error": "m3u8 URL not found after several attempts."}


