from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import configparser
import time
import logging

config = configparser.ConfigParser()

config.read('config.properties')

accounts_username = config.get('custom_parameters', 'accounts_username').split(',')
number_of_snap_to_send = int(config.get('custom_parameters', 'number_of_snap_to_send'))

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("logs/script.log"),
                              logging.StreamHandler()])

options = Options()
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.geolocation": 1,
    "profile.default_content_setting_values.notifications": 1
})

driver = webdriver.Chrome(options=options)

def multi_mode():
    try:
        photo_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'qJKfS')]"))
        )
        photo_button.click()
    except StaleElementReferenceException:
        time.sleep(2)
        photo_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'qJKfS')]"))
        )
        photo_button.click()
    
    time.sleep(2)

    for i in range(0, number_of_snap_to_send):
        while True:
            take_photo_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'FBYjn gK0xL A7Cr_ m3ODJ')]"))
            )
            take_photo_button.click()

            time.sleep(1)

            logs = driver.get_log('browser')

            error_found = any("Failed to create image/jpeg image Blob at quality 0.95" in log['message'] for log in logs)

            if not error_found:
                break

        send_to_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'YatIx fGS78 eKaL7 Bnaur')]"))
        )
        send_to_button.click()

        for username in accounts_username:
            user_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'RBx9s nonIntl') and contains(text(), '{username}')]"))
            )
            user_button.click()

        send_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='TYX6O eKaL7 Bnaur']"))
        )
        send_button.click()

        logging.info(f"Snap send to users")

def send_snap(username):
    photo_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[@class='cDumY EQJi_ rk6JA eKaL7 Bnaur' or @class='cDumY EQJi_ eKaL7 Bnaur']"))
    )
    photo_button.click()

    time.sleep(2)
    capture_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'FBYjn gK0xL A7Cr_')]"))
    )
    time.sleep(1)
    capture_button.click()

    send_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[@class='YatIx fGS78 eKaL7 Bnaur']"))
    )
    send_button.click()

    send_button2 = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[@class='TYX6O eKaL7 Bnaur']"))
    )
    send_button2.click()

    logging.info(f"Snap correctly send to {username}")

def send_snaps_to_user(username):
    try:
        user_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, f"//span[text()='{username}']"))
        )
        user_button.click()
    
        for i in range(0, number_of_snap_to_send):
            logging.info(f"A snap will be sent to to {username}")
            send_snap(username)
    except TimeoutException:
        logging.error(f"Unable to retrieve user with username {username}")

def mono_mode():
    for username in accounts_username:
        logging.info(f"Sending snaps to {username}")
        send_snaps_to_user(username)

logging.info(f"""
-----===============================================================================-----
 ______   __      _   _______   ______   _______   _        _______   __     __   ______
|  ____| |   \   | | |  ___  | |  __  | |  _____| | |      |  ___  | |  \   /  | |  ____|
| |____  | |\ \  | | | |___| | | |__| | | |___    | |      | |___| | |   \_/   | | |__
|____  | | | \ \ | | |  ___  | |  ____| |  ___|   | |      |  ___  | | |\   /| | |  __|
 ____| | | |  \ \| | | |   | | | |      | |       | |____  | |   | | | | \_/ | | | |____
|______| |_|   \___| |_|   |_| |_|      |_|       |______| |_|   |_| |_|     |_| |______|
-----======================================1.1======================================-----""")

try:
    driver.get('https://accounts.snapchat.com')

    cookies = [
        {
            "name": config.get('cookies', 'name_host_auth_session'), 
            "value": config.get('cookies', 'value_host_auth_session')
        },
        {
            "name": config.get('cookies', 'name_host_nonce'), 
            "value": config.get('cookies', 'value_host_nonce')
        }
    ]

    logging.debug(f"Defining snapchat cookies")

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.refresh()

    driver.get('https://www.snapchat.com')

    if config.get('custom_parameters', 'snap_mode') == 'MULTI':
        multi_mode()
    elif config.get('custom_parameters', 'snap_mode') == 'MONO':
        mono_mode()
    else:
        Exception

except Exception as e:
    logging.error(f"Une erreur est survenue : {e}")

finally:
    driver.quit()
