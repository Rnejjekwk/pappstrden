from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, json
from webdriver_manager.chrome import ChromeDriverManager

# Choose mode (TV or Movie)
mode = input("TV or Movie? (tv/movie): ").strip().lower()
if mode == "tv":
    show_id = input("TV Show ID (e.g. tt1234567): ").strip()
    season = input("Season (e.g. 1): ").strip()
    episode = input("Episode (e.g. 2): ").strip()
    url = f"https://player.videasy.net/tv/{show_id}/{season}/{episode}"
elif mode == "movie":
    movie_id = input("Movie Code (e.g. 786892): ").strip()
    url = f"https://player.videasy.net/movie/{movie_id}"
else:
    print("[x] Invalid option.")
    exit()

# Set up browser with devtools enabled using WebDriver Manager to handle chromedriver
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument("--mute-audio")
options.add_argument("--headless")  # Run headless (no browser UI)

# Initialize the Chrome WebDriver with WebDriver Manager
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

print(f"[→] Loading: {url}")
driver.get(url)
time.sleep(5)  # wait for player to fully load

# Click play button
try:
    button = driver.find_element(By.XPATH, "//button//*[name()='path' and contains(@d, 'M1.33398 8.00378')]")
    ActionChains(driver).move_to_element(button).click().perform()
    print("[✓] Play button clicked.")
except Exception as e:
    print(f"[!] Play button not found or already playing. Error: {e}")

# Continuously check for the m3u8 stream URL
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
                    print("\n[🎥 M3U8 FOUND] -->", url)
                    found = True
                    break
        except Exception as e:
            continue

# Once m3u8 is found, quit the driver
driver.quit()
