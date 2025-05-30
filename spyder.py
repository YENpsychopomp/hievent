import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import random
import barcode
from barcode.writer import ImageWriter

IMAGE_DIR = 'static\img'
os.makedirs(IMAGE_DIR, exist_ok=True)

# 商品分類對應的 listid
listids = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11', 'A12']
# listids = ['A01']
data = {}

# 單位列表，用於從商品名稱中提取單位
units = ['杯', '瓶', '包', '盒', '件']

def parse_product_info(name: str):
    # 品名範例："大杯美式2杯76元" 或 "買20送20"
    quantity = 1
    unit = '杯'
    price = 0

    # 嘗試解析「買X送X」
    match = re.search(r'買(\d+)送(\d+)', name)
    if match:
        quantity = int(match.group(1)) + int(match.group(2))
    else:
        # 嘗試解析「X杯」
        match = re.search(r'(\d+)杯', name)
        if match:
            quantity = int(match.group(1))

    # 解析價格
    match = re.search(r'(\d+)[元\$]', name)
    if match:
        price = int(match.group(1))

    # 擷取品項名稱（不含價格與數量）
    cleaned_name = re.sub(r'\d+杯|\d+[元\$]|買\d+送\d+', '', name)
    cleaned_name = cleaned_name.strip()

    return cleaned_name, quantity, price, unit

def generatorBarcode():
    with open('temp.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        oldBarcode = data.get("barcode")
        newBarcode = 0
        while True:
            newBarcode = "860200" + str(random.randint(1, 9999999)).zfill(7)
            if newBarcode in oldBarcode:
                continue
            oldBarcode.append(newBarcode)
            break

        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.truncate()

        ean = barcode.get_barcode_class('ean13')
        barcode_img = ean(newBarcode, writer=ImageWriter())
        output_path = os.path.join(IMAGE_DIR, newBarcode + '.png')
        barcode_img.save(output_path)

        return newBarcode
product_data = {}
# 遍歷每個分類頁面
for listid in listids:
    url = f'https://hievent.hilife.com.tw/HiShare/Menu/?listid=A10&page=2'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'無法取得 {url}')
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select('section.content .list-prd .list-prd-item')
    for item in items:
        body = item.select_one('.prd-body')
        name = body.select_one('.prd-title').text.strip() if body.select_one('.prd-title') else ''
        time = body.select_one('.prd-date').text.strip() if body.select_one('.prd-date') else ''
        category = soup.select_one('.navbar .navbar-nav .nav-item.active a').text.strip()
        # 取得圖片連結
        img_tag = item.select_one('img')
        img_url = img_tag['src'] if img_tag else ''

        if category not in product_data:
            product_data[category] = {}
        temp = parse_product_info(name)
        # 將資料以品名為 key 儲存
        if temp[2] == 0:
            print(temp[0])
        product_data[category][name] = [
            temp[1],
            temp[2],
            img_url.split("/")[-1].split("?")[0],
            temp[3],
            time.split("：")[1],
            generatorBarcode(),
        ]

# 儲存為 JSON 檔案
with open('appcoffee\data\productInfos.json', 'w', encoding='utf-8') as f:
    json.dump(product_data, f, ensure_ascii=False, indent=4)

print('資料已儲存至 products.json')
