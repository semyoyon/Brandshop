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




def login(session, email, password):
    session
    driver = webdriver.Firefox()
    url = "https://brandshop.ru/login/"
    driver.get(url)
    time.sleep(20)
    driver.find_element_by_id('login-id').send_keys(email)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_xpath("//form[@id='login-form']/button[1]").click()
    time.sleep(3)
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    headers1 = {
        'Host': 'brandshop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'}
    headers = {
        'Host': 'brandshop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '3327',
        'Origin': 'https://brandshop.ru',
        'Connection': 'keep-alive',
        'Referer': 'https://brandshop.ru/login/',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'}
    r = session.get("https://brandshop.ru/account/")
    # data = {"email": email,
    #         "password": password,
    #         "redirect": ""
    #         }
    # r = session.post("https://brandshop.ru/login/", data=data, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    print(soup)


def shipping_method(session, method):
    session.get('https://brandshop.ru/checkout/')

    data = {"shipping_method": method}
    r = session.post("https://brandshop.ru/index.php?route=checkout/checkout/setshippingmethod", data=data)
    data2 = {"payment_method": "payture"}
    r = session.post("https://brandshop.ru/index.php?route=checkout/checkout/setpaymentmethod", data=data2)
    r3 = session.get("https://brandshop.ru/checkout/")
    return(r3)



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

def getsession(u):
    print(u.text)
    soup = BeautifulSoup(u.text, 'html.parser')
    div = soup.find(id="request-data")
    print('###')
    print(div)
    print('###')
    print(div['value'])
    return(div['value'])



if __name__ == '__main__':
    s = requests.Session()
    login(s, "semkon@mail.ru", "11111111")

    product = infos("https://brandshop.ru/goods/250351/cm997hfk/", "42 EU")
    product_info = {"quantity": "1",
                "product_id": product[0],
                "option_value_id": product[2],
                product[3]: product[1]
                }

    add_to_cart = s.post("https://brandshop.ru/index.php?route=checkout/cart/add", data=product_info)
    print(add_to_cart)
    # r = s.get("https://brandshop.ru/checkout/")
    # print(r.text)
    # print(soup)
    unprep = shipping_method(s, 'cdek')
    prep = getsession(unprep)

    #
    # r2 = json.loads(add_to_cart.text)
    # print(r2)
    headers = {
        'Host': 'brandshop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': '393',
        'Origin': 'https://brandshop.ru',
        'Connection': 'keep-alive',
        'Referer': 'https://brandshop.ru/checkout/',
        'TE': 'Trailers'
        }
    data2 = {
        "Data": prep
    }
    ree = s.post("https://brandshop.ru/index.php?route=payment/payture/send", data=data2, headers=headers)
    print(ree)
    print(ree.text)









