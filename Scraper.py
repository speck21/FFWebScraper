import requests
import json
import time
import sys
import os
import aiosmtpd
from email.message import EmailMessage
from twilio.rest import Client
from bs4 import BeautifulSoup



def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_elements = soup.find_all(class_='boost-pfs-filter-product-item-title')
    products = [element.text.strip() for element in product_elements]
    return products

def load_product_list(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_products(filename, product_list):
    with open(filename, 'w') as file:
        json.dump(product_list, file)

def send_sms_alert(product):
    #Twilio account credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number=18664225176
    recipient_phone_number=16189722486

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'F**kface Merch Spotted: {product}',
        from_=twilio_phone_number,
        to=recipient_phone_number
    )

    print(f'SMS alert sent: {message.sid}')

async def email_alert(product):
    msg = EmailMessage()
    msg.set_content(f'F**kface Merch Spotted: {product}')
    msg['subject'] = 'FF Merch Alert'
    msg['to'] = os.environ.get('PHONEEMAIL')

    user = os.environ.get('FFEMAIL')
    password = os.environ.get('FFPASSWORD')

    server = aiosmtpd.asyncio


if __name__ == "__main__":
    
    filename = 'product-list.json'
    website_url = 'https://store.roosterteeth.com/collections/f-kface'    
    
    #load initial products
    initial_products = load_product_list(filename)

    while True:
        #Rescrape website
        current_products = scrape_website(website_url)

        for product in current_products:
            if product not in initial_products:
                send_sms_alert(product)
        #Save the new product list, rewriting removes deleted items
        save_products(filename, current_products)
        initial_products = current_products  
        for product in current_products:
            print(product)
            sys.stdout.flush()
        
        time.sleep(30)   



  
