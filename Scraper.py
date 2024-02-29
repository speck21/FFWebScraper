import requests
import json
import time
import sys
import os
import smtplib
import asyncio
import aiofiles
import aiohttp
from email.message import EmailMessage
# from twilio.rest import Client
from bs4 import BeautifulSoup


async def scrape_site(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            product_elements = soup.find_all(class_='boost-pfs-filter-product-item-title')
            products = [element.text.strip() for element in product_elements]
            return products

async def load_prod_list(filename):
    try:
        async with aiofiles.open(filename, 'r') as file:
            content = await file.read()
            return json.loads(content)
    except(FileNotFoundError, json.JSONDecodeError):
        return []

async def save_prod(filename, product_list):
    async with aiofiles.open(filename, 'w') as file:
        await file.write(json.dumps(product_list))

async def email_alert(products):
    msg = EmailMessage()
    msg.set_content(f'F**kface Merch Spotted: {products}')
    msg['subject'] = 'FF Merch Alert'
    msg['from'] = os.environ.get('FFEMAIL')
    msg['to'] = os.environ.get('PHONEEMAIL')

    user = os.environ.get('FFEMAIL')
    password = os.environ.get('AppPasswordSpeckTest')

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    print(f'Email to SMS message sent: {msg.get_payload}')
    server.quit()

async def main():
    filename = 'product-list.json'
    website_url = 'https://store.roosterteeth.com/collections/f-kface'    
    
    #load initial products
    initial_products = await load_prod_list(filename)

    while True:
        #Rescrape website
        current_products = await scrape_site(website_url)
        new_prod_list = []
        for product in current_products:
            if product not in initial_products:
                #Switching to email
                #send_sms_alert(product)
                #await email_alert(product)
                new_prod_list.append(product)
        if new_prod_list != []:
            await email_alert(new_prod_list)
                
        #Save the new product list, rewriting removes deleted items
        await save_prod(filename, current_products)
        initial_products = current_products  
        for product in current_products:
            print(product)
            sys.stdout.flush()
        
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

  
