from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import os, stat
import requests
import time
import logging
import platform


def main():
    correct_path = get_path_by_os()
    current_directory = os.getcwd() + correct_path + "temp"
    chrome_options = Options()

    # 不需開啟瀏覽器
    # chrome_options.add_argument('--headless=new')
    # chrome_options.add_argument('--no-sandbox')

    chrome_options.add_argument('--disable-extensions')
    prefs = {"download.default_directory": current_directory}
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.maximize_window()

    # Send a get request to the url
    driver.get('https://bi.elifemall.com.tw/')
    driver.implicitly_wait(15)
    # original_window = driver.current_window_handle

    try:
        logging_message("  " + os.environ['ACCOUNT'] + " login")
        # driver.find_element('name', 'username').send_keys(os.environ['ACCOUNT'])
        # driver.find_element('name', 'password').send_keys(os.environ['PASSWORD'])
        driver.find_element('name', 'username').send_keys("Administrator")
        driver.find_element('name', 'password').send_keys("!qazxsw23edc")
        driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[1]/div[2]/div/span/form/button').click()
        logging_message("  Login Success")
    except requests.exceptions.RequestException as e:
        logging_message(e)
        send_error_email()

    try:
        # user_content = driver.find_element(By.XPATH,
        #                                    '//*[@id="app-root"]/div/div[1]/div/div/div/div[2]/div[1]/div/div[2]/div[4]/div/button')
        user_content = driver.find_element(By.XPATH,
                                           '//*[@id="app-root"]/div/div[1]/div/div/div/div[2]/div[1]/div/div[2]/div[4]/div/button')
        driver.execute_script("arguments[0].click();", user_content)

        # setting = driver.find_element(By.XPATH, '//*[@id="app-root"]/div[2]/div/div/div/div[3]/div')
        setting = driver.find_element(By.XPATH, '//*[@id="app-root"]/div[2]/div/div/div/div[2]')
        driver.execute_script("arguments[0].click();", setting)
    except requests.exceptions.RequestException as e:
        logging_message(e)
        send_error_email()

    try:
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                '//*[@id="app-root"]/div/div[1]/div/div/div/div[2]/div[2]/div/div[3]/div/div/table/tbody[2]/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/div/table')))

        if table is not None:
            trs = WebDriverWait(table, 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//tr")))
            for i in range(len(trs)):
                if i > 0:
                    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                            '//*[@id="app-root"]/div/div[1]/div/div/div/div[2]/div[2]/div/div[3]/div/div/table/tbody[2]/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/div/table')))

                    trs = WebDriverWait(table, 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//tr")))
                    tds = WebDriverWait(trs[1], 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//td")))
                    last_td = tds[-1]

                    button = WebDriverWait(last_td, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[@class='f1duloxi high-density']")))
                    button.click()

                    remove = WebDriverWait(button, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="react-confirm-action-dialog-Dialog-Body-Id"]/div[2]/span/button')))
                    remove.click()
                    logging_message("  remove session")

                    time.sleep(10)
            logging_message("  Done")
        else:
            logging_message("  No items found")

    except requests.exceptions.RequestException as e:
        logging_message(e)
        send_error_email()
        pass
    except TimeoutException as e:
        logging_message("  No items found")
        logging_message("  Timeout")
        logging_message(e)
        pass

    driver.close()


def get_path_by_os():
    os_name = platform.system()
    if os_name == 'Windows':
        return '\\'
    else:
        return '/'


def logging_message(message):
    # print(message)
    logging.basicConfig(level=logging.INFO, filename='accesslog ' + time.strftime('%Y%m%d_%H_%M_%S') + '.log',
                        filemode='a', format='%(asctime)s %(levelname)s: %(message)s')
    logging.info(message)


def send_error_email():
    content = MIMEMultipart()
    content["subject"] = "elifemall test"
    content["from"] = "allen.chen@elifemall.com.tw"
    content["to"] = "allen.chen@elifemall.com.tw"
    content.attach(MIMEText("Tableau delete all session program execution error."))

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("allen.chen@elifemall.com.tw", "xfxvvbjmdltkjatt")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Send Error Notification to " + content["to"])
        except Exception as e:
            print("Error message: ", e)


if __name__ == '__main__':
    main()
