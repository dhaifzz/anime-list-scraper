from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import os

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.anime-planet.com/users/Username/anime/watched") # Replace 'Username' with the actual username or change the URL to the desired anime list page

wait = WebDriverWait(driver, 15)

titles = []
page_count = 0

while True:
    try:
        page_count += 1
        print(f"Loading page {page_count}...")
        
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-type='anime']")))
        time.sleep(2)
        
        items = driver.find_elements(By.CSS_SELECTOR, "[data-type='anime']")
        
        if not items:
            print("No items found with primary selector, trying fallback...")
            items = driver.find_elements(By.CLASS_NAME, "cardDeck-item")
        
        print(f"Found {len(items)} items on page {page_count}")
        
        for item in items:
            try:
                title = None
                try:
                    title = item.find_element(By.TAG_NAME, "h4").text
                except:
                    try:
                        title = item.find_element(By.CLASS_NAME, "cardName").text
                    except:
                        title = item.find_element(By.TAG_NAME, "a").text
                
                if title and title not in titles:
                    titles.append(title)
                    print(f"Added: {title}")
            except Exception as e:
                pass

        print(f"Total collected: {len(titles)}")

        try:
            pagination_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a, .paginate a")
            
            if pagination_links:
                next_link = None
                for link in pagination_links:
                    try:
                        page_num = int(link.text.strip())
                        if page_num == page_count + 1:
                            next_link = link
                            break
                    except:
                        pass
                
                if next_link and next_link.is_displayed():
                    print(f"Clicking page {page_count + 1}...")
                    driver.execute_script("arguments[0].click();", next_link)
                    time.sleep(3)
                else:
                    print("No more pages to scrape")
                    break
            else:
                print("No pagination found")
                break
        except Exception as e:
            print(f"Error with pagination: {e}")
            break

    except Exception as e:
        print(f"Error on page {page_count}: {e}")
        break

driver.quit()

# Save CSV in script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "anime_list.csv")

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title"])
    for t in titles:
        writer.writerow([t])

print(f"Done! Total titles collected: {len(titles)}")
print(f"Saved to: {csv_path}")

print("Done! Total:", len(titles))