from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

#

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36")


#
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#
url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=UZ&is_targeted_country=false&media_type=all&search_type=page&view_all_page_id=112462574687512"  # <-- вставь ссылку на нужную страницу
driver.get(url)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(15)


def get_texts():
    try:
        container_xpath = '/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div[5]/div[2]/div[2]/div[4]/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/span/div/div/div'
        f_t = ""
        creatives = []
        for i in range(1, 6):
            path = f"/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div[6]/div[2]/div[2]/div[4]/div[1]/div[{i}]/div/div[3]/div/div/div[2]/div[1]/span/div/div/div"
            container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, container_xpath)))
            creatives.append(f"{container.text}")
            # f_t += f"{container.text}\n\n--------------------\n\n"
        lst = set(creatives)
        return lst
    except Exception as e:
        url = (f"https://api.telegram.org/bot7605174176:AAEdzUKDE0bYrMWv-NA7HQaw3T6hQZXLll0/"
               f"sendMessage?chat_id=-1002695927579&text={e}")
        requests.get(url)
