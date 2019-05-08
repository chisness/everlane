from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pandas as pd
import numpy as np
import os 
import sys
import time
from selenium.common.exceptions import TimeoutException

driver = webdriver.Firefox()

mens_categories = ['https://www.everlane.com/collections/mens-jeans', 'https://www.everlane.com/collections/mens-bottoms', 
'https://www.everlane.com/collections/mens-shirt-shop', 'https://www.everlane.com/collections/mens-tees', 
'https://www.everlane.com/collections/mens-sweaters', 'https://www.everlane.com/collections/mens-outerwear',
'https://www.everlane.com/collections/mens-sweatshirts', 'https://www.everlane.com/collections/mens-shorts', 
'https://www.everlane.com/collections/mens-underwear', 'https://www.everlane.com/collections/mens-backpacks-bags', 
'https://www.everlane.com/collections/mens-hats', 'https://www.everlane.com/collections/mens-scarves']

def get_product_urls(url_categories, filename):

	product_urls = []
	
	for category in mens_categories:
	    driver.get(category)
	    html = driver.page_source
	    page_content = BeautifulSoup(html, features="lxml")

	    urls = page_content.find_all('div', class_='product-image product-image--4x5')
	    for url in urls:
	        product_urls.append('https://www.everlane.com' + url.find('a')['href'])
	    #urls = name.text.strip()
	    #name = name.rsplit(' — ')[0]
	
	product_urls.append('https://www.everlane.com/products/mens-tread-trainer-offwhite') #sole product in its category

	with open(filename, 'w') as f:
		for line in product_urls:
			f.write(line + '\n')
		f.close()

	#print('total product urls: ', len(product_urls))


def get_product_info(filename, start):
	with open(filename, 'r') as f:
		product_urls = f.read()

	#print(product_urls)
	product_urls = product_urls.split()

	items = []
	erroritems = []
	d = ['product', 'cost', 'everlane_price', 'sale', 'retail_price', 'url']
	#name_erroritems = []

	for i, product_url in enumerate(product_urls[start:]):
	    # if len(name_erroritems) > 15:
	    #     for line in name_erroritems: 
	    #         print(line)
	    #     break

	    name = ''
	    cost = 0.0
	    sale = False
	    everlane_price = 0.0
	    retail_price = 0.0

	    
	    #product_url = 'https://www.everlane.com/products/mens-nylon-duffel-pack-black?collection=mens-backpacks-bags'
	    print(product_url)
	    try: 
	    	driver.get(product_url)
	    	html = driver.page_source
	    	page_content = BeautifulSoup(html, features="lxml")
	    except TimeoutException:
	    	pass

	    name = page_content.find('h1', class_='product-heading__name')
	    #print(name)
	    if name is not None:
	        name = str(name.find('span', itemprop='name').contents[0])
	    else:
	        print('name error', product_url)
	        #name_erroritems.append(product_url)
	        #continue
	    #print(name)

	    cost = page_content.find('div', class_='infographic__true-cost')
	    if cost is not None:
	        cost = str(cost.find('p', class_='infographic__cost-text infographic__cost-text--price').contents[0])
	        cost = float(cost[1:])
	    else:
	        print('cost error', product_url)
	    #print(cost)



	    everlane_price = page_content.find('span', class_='product-heading__price-value') #regular item
	    if everlane_price is not None:
	        everlane_price = everlane_price.text.strip()
	        #everlane_price = retail_price.rsplit(None, 1)[-1]
	        everlane_price = float(everlane_price[1:])
	    else:
	        everlane_price = page_content.find('div', class_='product-page__choose-what-you-pay-price-controls clearfix') #item on sale
	        if everlane_price is not None:
	            everlane_price = str(everlane_price.find('button').contents[0])
	            everlane_price = float(everlane_price[1:])
	            sale = True
	        else: 
	            print('everlane_price error', product_url)
	    #print(everlane_price)

	    retail_price = page_content.find('div', class_='product-heading__traditional-price')
	    if retail_price is not None:
	        retail_price = retail_price.text.strip()
	        retail_price = retail_price.rsplit(None, 1)[-1] #gets last item in the text
	        retail_price = float(retail_price[1:])
	        #print(retail_price)
	    else:
	        print('retail_price error', product_url)

	    item = [name, cost, everlane_price, sale, retail_price, product_url]
	    if item.count(None) == 0:
	    	#item.extend([everlane_price / cost, retail_price/cost, retail_price/everlane_price])
	        items.append(item)
	    else:
	        erroritems.append(item)

	    if i%20 == 0 and i>0:
	    	time.sleep(300)
	    	df = pd.DataFrame(columns = d, data = items)
	    	df['everlane_markup'] = df['everlane_price']/df['cost']
	    	df['retail_markup'] = df['retail_price']/df['cost']
	    	df['retail_to_everlane'] = df['retail_price']/df['everlane_price']
	    	df.to_csv('everlaned.csv')
	    	print(i+start)
	    	print(df)


	# with open('results.txt', 'w') as f:
	# 	for line in items:
	# 		f.write(line + '\n')

	#value_items = sorted(items, key=lambda x: x[-3])
	#print(value_items)

	   



#get_product_urls(mens_categories, 'sample.txt')
get_product_info('sample.txt', 0)


