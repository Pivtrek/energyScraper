from collections import defaultdict
import elicznik
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time, re

"""
@:param start_date - date when we want to start gathering data
@:param end_date - date when we want to stop gathering data
example: start_date - 01.06.2024, end_date - 01.06.2023
@:param username - tauron elicznik username
@:param password - tauron elicznik password
@:return energy - defaultdict with "consumption" and "production" keys with date - energy[date]['production']
"""

def tauron_scraper(start_date, end_date, username, password):
    #there is yearly pagination in tauron API so it has to be as many requests as years beetween start and end date
    delta_date = start_date
    readings = []
    with elicznik.ELicznik(username, password, "optional_site_identifier") as m:
        while delta_date > end_date:
            if((delta_date-end_date).days > 365):
                readings.append(m.get_readings((delta_date - relativedelta(days=364)), delta_date))
                delta_date = delta_date - relativedelta(days=365)
            else:
                readings.append(m.get_readings(end_date, delta_date))#last request
                delta_date = delta_date - relativedelta(days=365)

    energy = defaultdict(lambda: {"consumption": 0.0, "production": 0.0})

    for reading in readings:
        date = reading.timestamp.date()
        energy[date]["consumption"] += reading.consumption
        energy[date]["production"] += reading.production

    return energy

"""
@:param end_date - to which date you want to gather yield
@:param fusion_login, fusion_password - login credentials do huaweii website
@:return saved_yield - dictionary for yield with date as key and yield as value
"""

def fusion_solar_scraper(end_date, fusion_login, fusion_password):

    #login credentials
    fusionsolar_url = "https://eu5.fusionsolar.huawei.com"

    #preparing website options to run it properly
    options = Options()
    options.add_experimental_option("detach", True)
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')  #headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("window-size=1920,1080") #setting windows size to click buttons properly

    #log in website
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(fusionsolar_url)

    #click need to put username and password
    time.sleep(3.0)
    ac = ActionChains(driver)
    ac.move_by_offset(1888,121).click()

    #log in

    username = driver.find_element(By.ID,"username")
    username.send_keys(fusion_login)
    password = driver.find_element(By.ID, "value")
    password.send_keys(fusion_password)

    login_button = driver.find_element(By.ID, "submitDataverify")
    login_button.click()
    time.sleep(25.0)#estimeted time to load whole website after login in

    #compute clicks based on dates delta
    current_date = datetime.strptime((driver.find_element(By.XPATH, "//input[@placeholder='Select date']").get_attribute("title")), "%Y-%m-%d")
    delta = current_date - end_date

    #dictionary for yield with date as key and yield as value
    saved_yield = {}

    max_retries = 50

    for i in range(delta.days):
        for attempt in range(max_retries):
            try:
                key = driver.find_element(By.XPATH, "//input[@placeholder='Select date']").get_attribute("title")
                value = driver.find_element(By.CLASS_NAME,"nco-product-power-center").get_attribute("title")
                number = re.search(r'\d+\.\d+', value)
                if number is not None:
                    saved_yield[key] = float(number.group())
                else:
                    saved_yield[key] = 0.0
                left_arrow_button = driver.find_element(By.XPATH,"//*[@title='Previous day']")
                left_arrow_button.click()
                time.sleep(0.9)
                print(i)
                break
            except NoSuchElementException as e:
                print(f"Wystąpił błąd: {e}. Próba numer {attempt + 1} z {max_retries}.")
                if attempt < max_retries - 1:
                    print("Czekam 2 sekundy przed ponowną próbą...")
                time.sleep(1)
            else:
                print("Osiągnięto maksymalną liczbę prób. Kończę program.")


    return saved_yield