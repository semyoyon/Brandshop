import requests
import json
from bs4 import BeautifulSoup
import lxml
import re
import json
import time


def login(session, email, password):
    session.get("https://brandshop.ru/login/")
    time.sleep(6)
    data = {"email": email,
            "password": password,
            "redirect": ""
            }
    x = session.post("https://brandshop.ru/login/", data=data)
    print(x.text)


def shipping_method(session, method):

    data = {"shipping_method": method}
    r = session.post("https://brandshop.ru/index.php?route=checkout/checkout/setshippingmethod", data=data)
    link = session.get("https://brandshop.ru/checkout/")
    soup = BeautifulSoup(link.text, 'html.parser')
    print(soup)

    r2 = json.loads(r.text)
    print(r2)

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



if __name__ == '__main__':
    s = requests.Session()
    login(s, "semyoyon@gmail.com", "Hy&43j01")

    product = infos("https://brandshop.ru/goods/250351/cm997hfk/", "42 EU")
    product_info = {"quantity": "1",
                "product_id": product[0],
                "option_value_id": product[2],
                product[3]: product[1]
                }

    add_to_cart = s.post("https://brandshop.ru/index.php?route=checkout/cart/add", data=product_info)
    r2 = json.loads(add_to_cart.text)
    print(r2)










