import requests
import json
from bs4 import BeautifulSoup
import lxml
import re
import json
import time
import js2py
import base64
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def wait_until_clickable(driver, xpath=None, class_name=None, duration=10000000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))


def wait_until_visible(driver, xpath=None, class_name=None, duration=10000000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))

def login(session, email, password):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    url = "https://brandshop.ru/login/"
    driver.get(url)
    wait_until_visible(driver=driver, xpath="//input[@id='login-id']")
    email_input = driver.find_element_by_xpath("//input[@id='login-id']")
    email_input.clear()
    email_input.send_keys(email)
    wait_until_visible(driver=driver, xpath="//input[@id='password']")
    password_input = driver.find_element_by_xpath("//input[@id='password']")
    password_input.clear()
    password_input.send_keys(password)
    wait_until_clickable(driver=driver, xpath="//form[@id='login-form']/button[1]")
    submit = driver.find_element_by_xpath("//form[@id='login-form']/button[1]")
    submit.click()
    wait_until_visible(driver=driver, xpath="//p[text()='Мои заказы']")
    cookies = driver.get_cookies()
    driver.quit()

    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    r = session.get("https://brandshop.ru/account/")
    # data = {"email": email,
    #         "password": password,
    #         "redirect": ""
    #         }
    # r = session.post("https://brandshop.ru/login/", data=data, headers=headers)

    # html = r.text
    # soup = BeautifulSoup(html, 'lxml')
    # print(soup)

def infos(link, size):
    link = requests.get(link)
    soup = BeautifulSoup(link.text, 'html.parser')
    title = soup.find("meta", itemprop="productID") # находим id продукта для 2 параметра
    #print(title["content"])

    scores = soup.find_all(text=re.compile(size))
    divs = [sizeselect.parent for sizeselect in scores]

    #print(divs[0]['data-option-id']) # значение для 4 параметра
    #print(divs[0]['data-option-value-id']) # значение для 3 параметра

    a = soup.find("input", {"id": "product-size"}) # 4 параметр
    #print(a["name"])

    return (title["content"], divs[0]['data-option-id'], divs[0]['data-option-value-id'], a["name"])

def add_to_cart(session, product):
    product_info = {"quantity": "1",
                    "product_id": product[0],
                    "option_value_id": product[2],
                    product[3]: product[1]
                    }
    session.post("https://brandshop.ru/index.php?route=checkout/cart/add", data=product_info)


def checkout(session, s_method, p_method):
    session.get('https://brandshop.ru/checkout/')
    data = {"shipping_method": s_method}
    r = session.post("https://brandshop.ru/index.php?route=checkout/checkout/setshippingmethod", data=data)
    data2 = {"payment_method": p_method}
    r2 = session.post("https://brandshop.ru/index.php?route=checkout/checkout/setpaymentmethod", data=data2)
    r3 = session.get("https://brandshop.ru/checkout/")
    return(r3)

def sessionid(u):
    print(u.text)
    soup = BeautifulSoup(u.text, 'html.parser')
    div = soup.find(id="request-data")
    print('###')
    print(div)
    print('###')
    print(div['value'])
    return(div['value'])

def checkoutlink(session, sessionid):
    data = {
        "Data": sessionid
    }
    r = session.post("https://brandshop.ru/index.php?route=payment/payture/send", data=data)
    print(r.text[12:-2].replace('\\',''))





if __name__ == '__main__':
    s = requests.Session()

    login(s, "semkon@mail.ru", "11111111")
    product = infos("https://brandshop.ru/goods/250351/cm997hfk/", "42 EU")
    add_to_cart(s, product)
    select = checkout(s, 'cdek', 'payture')
    prep = sessionid(select)
    checkoutlink(s, prep)

    #
    # r2 = json.loads(add_to_cart.text)
    # print(r2)
    # headers = {
    #     'Host': 'brandshop.ru',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
    #     'Accept': 'application/json, text/javascript, */*; q=0.01',
    #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #     'X-Requested-With': 'XMLHttpRequest',
    #     'Content-Length': '393',
    #     'Origin': 'https://brandshop.ru',
    #     'Connection': 'keep-alive',
    #     'Referer': 'https://brandshop.ru/checkout/',
    #     'TE': 'Trailers'
    #     }









