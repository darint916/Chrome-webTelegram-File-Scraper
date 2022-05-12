from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
page = requests.get("https://web.telegram.org/z/#-1725878819")

soup = BeautifulSoup(page.content, 'html.parser')
#For headless no gui
options = webdriver.ChromeOptions()
#options.headless = True
#options.add_argument("--window-size=")
options.add_experimental_option("detach", True)

#Personal info
DRIVER_PATH = 'PATH_TO_DRIVER'
telegram_page_link = 'LINK'
phone_number = "PHONE NUMBER"


driver = webdriver.Chrome(chrome_options=options, executable_path=DRIVER_PATH)
driver.get(telegram_page_link)

time.sleep(6)
login_click = driver.find_element_by_css_selector('#auth-qr-form > div > button')
login_click.click()
time.sleep(1)
input_phone_num = driver.find_element_by_css_selector('#sign-in-phone-number')
input_phone_num.send_keys(phone_number)
#driver.find_element_by_css_selector('#sign-in-keep-session').click()
time.sleep(3)
next_button = driver.find_element_by_css_selector('#auth-phone-number-form > div > form > button:nth-child(4)').click()
time.sleep(5)
phone_code = input("Enter in phone number val: ")
driver.find_element_by_css_selector('#sign-in-code').send_keys(phone_code)
time.sleep(3)
try:
    driver.navigate().to(telegram_page_link)
except:
    try:
        driver.find_element_by_css_selector('#LeftColumn-main > div.Transition.zoom-fade > div > div > div > div > div > div > div.ListItem.Chat.chat-item-clickable.group.selected.no-selection.has-ripple').click()
    except:
        print("Error click")
        driver.find_element_by_css_selector("#LeftColumn-main > div.Transition.zoom-fade > div > div > div > div > div > div > div.ListItem.Chat.chat-item-clickable.group.selected.no-selection.has-ripple > div > div.ripple-container").click()
    
    print("failed")
time.sleep(10)
