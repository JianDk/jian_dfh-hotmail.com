from selenium  import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import os
import time

chrome_options = Options()
chrome_options.headless = False
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--window-size=1920x1080")
currentPath = os.getcwd()
driverpath = os.path.join(currentPath, "headless_chrome", "chromedriver")

driver = webdriver.Chrome(options = chrome_options, executable_path=driverpath)
driver.get("https://accounts.shopify.com/store-login")
print('browser initiated in hidden mode')
wait = WebDriverWait(driver, 30)
wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="shop_domain"]'),
    )).send_keys("dimsumshop.dk")

#Login
wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="body-content"]/div[1]/div[2]/div/form/button'),
)).click()

wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="account_email"]'),
)).send_keys("kontakt@dimsum.dk")

time.sleep(2)
wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="body-content"]/div[1]/div[2]/div/form/button'),
)).click()

#input password
