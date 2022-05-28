from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import json
import threading
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#from bs4 import BeautifulSoup
import time
import requests
page = requests.get("https://web.telegram.org/z/")
#For headless no gui
options = Options()
options.add_argument("start-maximized")
#options.headless = True
#options.add_argument("--window-size=")
options.add_experimental_option("detach", True)

f = open('personal.json')
data = json.load(f)

s = Service(data['DRIVER_PATH'])
"""
Initial telegram login sequence
"""
driver = webdriver.Chrome(service=s, options=options)
driver.get(data['telegram_page_link'])
driver.execute_script("document.body.style.zoom='100%'")
time.sleep(7)
login_click = driver.find_element(By.CSS_SELECTOR, value='#auth-qr-form > div > button')
login_click.click()
time.sleep(2)
driver.find_element(By.CSS_SELECTOR, value='#sign-in-phone-number').send_keys(data['phone_number'])

#driver.find_element_by_css_selector('#sign-in-keep-session').click()
time.sleep(3.5)
driver.find_element(By.CSS_SELECTOR, value='#auth-phone-number-form > div > form > button:nth-child(4)').click()
time.sleep(3.5)
phone_code = input("Enter in phone number val: ")
try:
    driver.find_element(By.CSS_SELECTOR, value='#sign-in-code').send_keys(phone_code)
except:
    pass
time.sleep(3.5)
driver.find_elements(By.CLASS_NAME, value="ListItem")[data['group_option'] - 1].click()

def get_file_size(msg: WebElement): 
    try:
        size: WebElement = msg.find_element(By.CLASS_NAME, value="file-subtitle")
    except:
        print("No size")
        return None
    file_size, unit = size.text.split(" ")
    file_size = float(file_size)
    if unit == "MB":
        return file_size * 1024
    elif unit == "KB":
        return file_size

def get_file_title(msg: WebElement):
    try:
        title: WebElement = msg.find_element(By.CLASS_NAME, value="file-title")
        return title.text
    except:
        print("No title")
        return None

def remind_msg():
    print("\nConfig Reminder:\nR = RefreshTime")
    print("M = Data Mod: 0 for group_page, 1 for last_msg")

global msg_sequence
msg_sequence = {}
global wait_flag
wait_flag = False
global data_report
data_report = {"success": 0, "ignored": 0, "failed": 0}
remind_count = 0

"""Scrapes images queued from telegram group"""
def scrape_images():
    while True:
        global remind_count
        if remind_count > 3:
            remind_msg()
            remind_count = 0
        time.sleep(data['script_refresh_time'])
        msgs = driver.find_elements(By.CLASS_NAME, value="Message")
        for msg in msgs:
            try: 
                msg_id = int(msg.get_attribute("data-message-id"))
            except:
                continue
            #print(f"msg_id found: {msg_id}")
            if msg_id > data['last_msg_id']:
                msg_sequence.update({msg_id: msg})
                print(f"Queued msg: {msg_id}")
        print(f"Last msg found: {msg_id}")
        if(not list(msg_sequence.keys())):
            remind_count += 1
            print("No new messages")
            continue
        data['last_msg_id'] = max(msg_sequence.keys())
        item: WebElement = None
        wait_flag = True
        for key, item in msg_sequence.items():
            print(f"Attempting download of id {key}")
            if(name := get_file_title(item)):
                if(size := get_file_size(item)):
                    #print(f"Attempting download of {name} id: {key} - size:{size}")
                    try:
                        dl = item.find_element(By.CLASS_NAME, value="icon-download")
                        dl.click()
                        print(f"Download success, in progress{name} key: {key} - size:{size}")
                        data_report['success'] += 1
                        time.sleep(2)
                    except Exception as err:
                        try:
                            item.find_element(By.CLASS_NAME, value="icon-eye")
                            print(f"small file, skipping download. id: {key} - size:{size}")
                            data_report['ignored'] += 1
                        except:
                            print(f"Unable to find download button for id: {key}")
                            data_report['failed'] += 1
        wait_flag = False
        msg_sequence.clear()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        remind_msg()
        print(f"\nSequence end- Summary - Successes: {data_report['success']}, Ignored: {data_report['ignored']}, Failed: {data_report['failed']}\n\n")

def scroll_down_check():
    try:
        scroll_button = driver.find_element(By.CSS_SELECTOR, value ="#MiddleColumn > div.messages-layout > div.src-components-middle-FloatingActionButtons-module__root.src-components-middle-FloatingActionButtons-module__revealed.src-components-middle-FloatingActionButtons-module__no-composer.src-components-middle-FloatingActionButtons-module__no-extra-shift > div > button")
        scroll_button.click()
        print("scroll found")
    except:
        pass

"""Config wait selections"""
def debug_wait_timer():
    while not wait_flag:
        try:
            wait_input = input("Press M for data modification, R for timer/refresh time\n")
            wait_input.upper()
            if(wait_input == "M"):
                mod_input = input("Enter in selection: 0 -group_page option, 1 -last_msg_id\n")
                if(mod_input == "0"):
                    data['group_option'] = int(input("Enter in new group_option:\n"))
                    driver.find_elements(By.CLASS_NAME, value="ListItem")[data['group_option'] - 1].click()
                elif(mod_input == "1"):
                    data['last_msg_id'] = int(input("Enter in new last_msg_id:\n"))
                    print("Update Success, please wait for next refresh")
            elif(wait_input == "R"):
                data['script_refresh_time'] = int(input("Enter in new wait/refresh time:\n"))
        except:
            print("Invalid input, restarting config")
            continue
    time.sleep(2)
    debug_wait_timer()

print("Begin thread and scrape")
time.sleep(1)
downtime_timer = threading.Thread(target=debug_wait_timer)
downtime_timer.start()
scrape_images()

