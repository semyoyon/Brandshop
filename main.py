import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import threading
import json
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login_r(session, email, password):
    data = {"email": email,
            "password": password,
            "redirect": ""
            }
    session.post("https://95.217.195.88/login/", data=data, verify=False)

def getSizes(productLink):
    link = requests.get(productLink)
    soup = BeautifulSoup(link.text, 'html.parser')
    scores = soup.findAll("div", {"class": "sizeselect"})
    list = [i.string for i in scores]
    return list

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


def win_webhook(email, price, date, webhook_input):
    webhook = DiscordWebhook(url=webhook_input, username="Brandshop Preorder Bot")
    embed = DiscordEmbed(title=':tada:ПОБЕДА!:tada:', description=email, color=39368)
    embed.set_footer(text='BS v0.9')
    embed.set_timestamp()
    embed.add_embed_field(name='Price', value=price, inline=True)
    embed.add_embed_field(name='Date', value=date, inline=True)
    webhook.add_embed(embed)
    response = webhook.execute()
    print("Вебхук послан для: " + email)


def win_check(session, price, date):
    link = session.get("https://95.217.195.88/order/")
    soup = BeautifulSoup(link.text, 'html.parser')
    try:
        orders = soup.find('div', {"class": "row no-gutters order-heading"})
        datein = orders.find('div', {"class": "col col-2 col-sm-12 order-sm-3"})
        pricein = orders.find('div', {'class': 'col col-2 col-sm-12 hidden-sm'})

        if date == datein.text and price == re.sub(r',', '', pricein.text)[:-5]:
            return 'win'
            print('Победа!')
        else:
            print('Проигрыш!')
    except AttributeError:
        print("На аккаунте нет заказов")


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


def go_win(email, password, price, date, webhook_input):
    s = requests.Session()
    login_r(s, email, str(password))
    if win_check(s, price, date) == 'win':
        win_webhook(email, price, date, webhook_input)


if __name__ == '__main__':
    mode = input("Выберите режим:\n(1) Регистрация предзаказа\n(2) Чекер побед\n")

    if int(mode) == 1:
        link = input("Введите ссылку на продукт: ")
        print("\nДоступны размеры: ")
        print('\n'.join(getSizes(link)))
        size = input("\nВведите размер в формате '40': ") + " EU"
        delivery = input("\nВыберите метод доставки:\n(1) Для предзаказов 'pickup'\n(2) Для доставки 'flat'\n")
        if int(delivery) == 1:
            delivery = "pickup"
        if int(delivery) == 2:
            delivery = "flat"
        
        with open('webhook.json') as json_file:
            data = json.load(json_file)
            webhook_input = data['webhook']

        with open('accounts.json') as json_file:
            data = json.load(json_file)
            for p in data['accounts']:
                x = threading.Thread(target=go, args=(p['email'], p['password'], link, size, delivery, webhook_input))
                x.start()
                time.sleep(5)

    if int(mode) == 2:
        price = input("Введите цену: ")
        date = input("Введите дату в формате 01.01.1990: ")
        with open('webhook.json') as json_file:
            data = json.load(json_file)
            webhook_input = data['webhook']

        with open('accounts.json') as json_file:
            data = json.load(json_file)
            for p in data['accounts']:
                x = threading.Thread(target=go_win, args=(p['email'], p['password'], price, date, webhook_input))
                x.start()
                time.sleep(5)
