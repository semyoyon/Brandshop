import requests
from bs4 import BeautifulSoup
import re
from discord_webhook import DiscordWebhook, DiscordEmbed
import csv
import time
import threading
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By


# def wait_until_clickable(driver, xpath=None, class_name=None, duration=10000000, frequency=0.01):
#     if xpath:
#         WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
#     elif class_name:
#         WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
#
#
# def wait_until_visible(driver, xpath=None, class_name=None, duration=10000000, frequency=0.01):
#     if xpath:
#         WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
#     elif class_name:
#         WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
#
#
# def login(session, email, password):
#     options = Options()
#     #options = webdriver.ChromeOptions()
#     #options.add_argument("start-maximized")
#     #options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     #options.add_experimental_option('useAutomationExtension', False)
#     options.headless = False
#     #driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\Semyon\PycharmProjects\Brandshop\chromedriver.exe')
#     driver = webdriver.Firefox(options=options)
#     #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     #driver.execute_cdp_cmd('Network.setUserAgentOverride', {
#         #"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'})
#     #print(driver.execute_script("return navigator.userAgent;"))
#     url = "https://95.217.195.88/login"
#     driver.get(url)
#     #time.sleep(20)
#     wait_until_visible(driver=driver, xpath="//input[@id='login-id']")
#     email_input = driver.find_element_by_xpath("//input[@id='login-id']")
#     email_input.clear()
#     email_input.send_keys(email)
#     wait_until_visible(driver=driver, xpath="//input[@id='password']")
#     password_input = driver.find_element_by_xpath("//input[@id='password']")
#     password_input.clear()
#     password_input.send_keys(password)
#     wait_until_clickable(driver=driver, xpath="//form[@id='login-form']/button[1]")
#     submit = driver.find_element_by_xpath("//form[@id='login-form']/button[1]")
#     submit.click()
#     wait_until_visible(driver=driver, xpath="//p[text()='Персональные данные']")
#     cookies = driver.get_cookies()
#
#     driver.quit()
#
#     for cookie in cookies:
#         session.cookies.set(cookie['name'], cookie['value'])
#     r = session.get("https://brandshop.ru/account/")
#     # data = {"email": email,
#     #         "password": password,
#     #         "redirect": ""
#     #         }
#     # r = session.post("https://brandshop.ru/login/", data=data, headers=headers)
#
#     # html = r.text
#     # soup = BeautifulSoup(html, 'lxml')
#     # print(soup)
#

def login_r(session, email, password):
    data = {"email": email,
            "password": password,
            "redirect": ""
            }
    session.post("https://95.217.195.88/login/", data=data, verify=False)


def infos(link, size):
    link = requests.get(link)
    soup = BeautifulSoup(link.text, 'html.parser')
    title = soup.find("meta", itemprop="productID")  # находим id продукта для 2 параметра
    scores = soup.find_all(text=re.compile(size))
    divs = [sizeselect.parent for sizeselect in scores]
    a = soup.find("input", {"id": "product-size"})  # 4 параметр
    return (title["content"], divs[0]['data-option-id'], divs[0]['data-option-value-id'], a["name"])


def add_to_cart(session, product):
    product_info = {"quantity": "1",
                    "product_id": product[0],
                    "option_value_id": product[2],
                    product[3]: product[1]
                    }
    session.post("https://95.217.195.88/index.php?route=checkout/cart/add/", data=product_info)


def checkout(session, s_method, p_method):
    session.get('https://95.217.195.88/checkout/', verify=False)
    data = {"shipping_method": s_method}
    session.post("https://95.217.195.88/index.php?route=checkout/checkout/setshippingmethod", data=data, verify=False)
    data2 = {"payment_method": p_method}
    session.post("https://95.217.195.88/index.php?route=checkout/checkout/setpaymentmethod", data=data2, verify=False)
    r = session.get("https://95.217.195.88/checkout/", verify=False)
    return r


def sessionid(u):
    soup = BeautifulSoup(u.text, 'html.parser')
    div = soup.find(id="request-data")
    img = soup.find('div', {"class": "col col-3 col-sm-3"}).img['src']
    result = ''
    for wrapper in soup.findAll("div", {"class": "col col-6 sum"}):
        if wrapper.text != 'Итого':
            result = wrapper.text
    return div['value'], img, result


def checkoutlink(session, sessionid):
    data = {"Data": sessionid}
    r = session.post("https://95.217.195.88/index.php?route=payment/payture/send", data=data)
    return r.text[12:-2].replace('\\', '')


def webhook(email, link, size, img, price, webhook_input):
    # webhook = DiscordWebhook(url=webhook_input, content=link)
    # embed = DiscordEmbed(title=email, description='Brandshop Preorder Bot', color=242424)
    # embed.set_author(name='Author Name')
    # webhook.add_embed(embed)
    # webhook.execute()
    webhook = DiscordWebhook(url=webhook_input, username="Brandshop Preorder Bot")
    embed = DiscordEmbed(title=email, url=link, color=39368)
    embed.set_footer(text='BS v0.9')
    embed.set_timestamp()
    embed.add_embed_field(name='Size', value=size, inline=True)
    embed.add_embed_field(name='Price', value=price, inline=True)
    embed.set_thumbnail(url=img)

    webhook.add_embed(embed)
    response = webhook.execute()
    print("Вебхук послан для: " + email)


def go(email, password, link, size, delivery, webhook_input):
    s = requests.Session()
    login_r(s, email, str(password))
    product = infos(link, size)
    add_to_cart(s, product)
    select = checkout(s, delivery, 'payture')
    prep = sessionid(select)[0]
    link = checkoutlink(s, prep)
    img = sessionid(select)[1]
    price = sessionid(select)[2]
    webhook(email, link, size, img, price, webhook_input)


if __name__ == '__main__':
    link = input("Введите ссылку на продукт: ")
    size = input("Введите размер: ") + " EU"
    delivery = input("Введите метод доставки (для предзаказов 'pickup', для доставки 'flat'): ")
    with open('webhook.json') as json_file:
        data = json.load(json_file)
        webhook_input = data['webhook']

    with open('accounts.json') as json_file:
        data = json.load(json_file)
        for p in data['accounts']:
            x = threading.Thread(target=go, args=(p['email'], p['password'], link, size, delivery, webhook_input))
            x.start()
            time.sleep(5)
    # with open('bs.csv', 'r') as file:
    #     reader = csv.reader(file, delimiter=';')
    #     for row in reader:
    #         x = threading.Thread(target=go, args=(row[0], row[1], link, size, delivery, webhook_input))
    #         x.start()
    #         time.sleep(5)



    # start_time = time.time()
    # s = requests.Session()
    # login_r(s, "sema7@sksnkrs.club", "Alkash228")
    # product = infos("https://brandshop.ru/goods/249704/cd5436-100/", "40.5 EU")
    # add_to_cart(s, product)
    # select = checkout(s, 'flat', 'payture')
    # prep = sessionid(select)
    # link = checkoutlink(s, prep)
    # webhook('semkon@mail.ru', link, 'https://discordapp.com/api/webhooks/743404457647145010/IJ7__6trZSde5qFvKH_t7csAer3GUha6WceZ72t7UnX1XPMzKWIOokpPz_sX7oIF5zDJ')
    #
    # print("--- %s seconds ---" % (time.time() - start_time))

