from selenium  import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import os

chrome_options = Options()
#chrome_options.headless = True
chrome_options.add_experimental_option("detach", False)
chrome_options.add_argument("--window-size=1920x1080")
currentPath = os.getcwd()
driverpath = os.path.join(currentPath, "headless_chrome", "chromedriver")

driver = webdriver.Chrome(chrome_options = chrome_options, executable_path=driverpath)
driver.get('https://jian-xiong-wu.myshopify.com/admin/orders/2074671710339')
wait = WebDriverWait(driver, 30)
wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="body-content"]/div[1]/div[2]/div/form/button'),
    ))

#Login
elem = driver.find_element_by_xpath('//*[@id="account_email"]')
elem.send_keys("jian_dfh@hotmail.com")
wait.until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/form/button'),)).click()

wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="account_password"]')
)).send_keys("PASSport1")
wait.until(ec.element_to_be_clickable(
    (By.XPATH, '//*[@id="login_form"]/button'),
)).click()

#Locate the Delivery date and time frame
wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="note-attributes"]/div[2]/div[2]/div/div[3]/div'),
))

date = driver.find_element_by_xpath('//*[@id="note-attributes"]/div[2]/div[2]/div/div[3]/div').text

wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="note-attributes"]/div[2]/div[2]/div/div[4]/div'),))
timeframe = driver.find_element_by_xpath('//*[@id="note-attributes"]/div[2]/div[2]/div/div[4]/div').text
print(date, timeframe, sep = '---')