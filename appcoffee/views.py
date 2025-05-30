from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from .linePayHelper import getPaymentUrl
from .encryption import *
from .operationDatabase import *


import json
import os
import re
import random
import time
# Create your views here.
ENCRYPT_KEY = b'9364009534950706'

def index(request):
    return render(request, 'index.html', {
    'title':"萊爾富 | 來送禮",
    'data':"Version: 0.1.0",
    'now':datetime.now()
} )

def getProducts(request):
    """處理用戶端請求，回傳對應商品群組的商品資訊。

    接收 POST 請求，從 request body 中解析 JSON 內容，取得群組名稱（group）。
    根據群組名稱讀取 `productInfo.json` 中的對應商品資料，並以 JSON 格式回傳。

    Args:
        request (HttpRequest): Django 傳入的 HTTP 請求物件，預期為 POST 並含有 JSON 格式的資料。

    Returns:
        JsonResponse: 
            - 成功時回傳對應群組的商品資訊，格式為 {"commodityInfo": {...}}。
            - 若發生錯誤，回傳包含錯誤訊息的 JSON，如 {"error": "訊息"}，並附帶對應的 HTTP 狀態碼。
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        data = json.loads(request.body.decode("utf-8"))
        groupName = data.get("group", "")
        result = get_product_info_by_group(groupName)
        productInfo = {}
        if not result:
             return JsonResponse({"error": f"Group '{groupName}' not found"}, status=404)

        for item in result:
            productInfo[item["name"]] = {
                "quantity": item["quentity"],
                "price": item["price"],
                "img_path": item["img_path"],
                "unit": item["unit"],
                "time": item["time"],
                "barcode_path": item["barcode_path"],
                "description": item["description"]
            }
        return JsonResponse({"commodityInfo": productInfo}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def linePayUrl(request):
    """處理用戶付款請求並回傳 LINE Pay 付款網址。

    接收 POST 請求，從 request 的 JSON 資料中擷取 group 與 product，  
    依據商品名稱解析對應產品，並從 productInfo.json 中讀取商品資訊，  
    加密條碼後產生付款網址，最後回傳至前端。

    Args:
        request (HttpRequest): 來自前端的 POST 請求，包含 group 和 product 的 JSON 資料。

    Returns:
        JsonResponse: 包含付款網址的 JSON 物件，或錯誤訊息與 HTTP 狀態碼。
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        data = json.loads(request.body.decode("utf-8"))
        groupName = data.get("group", "")
        productName = data.get("product", "")
        email = data.get("email", "")

        jsonPath = os.path.join(settings.BASE_DIR, "appcoffee", "data", "productInfo.json")
        with open(jsonPath, "r", encoding="utf-8") as file:
            jsonData = json.load(file)

        productInfo = jsonData.get(groupName, {}).get(productName)

        if not productInfo:
            return JsonResponse({"error": "Product not found"}, status=404)

        try:
            encryptedBarcode = encrypt(int(productInfo[5]), ENCRYPT_KEY)
            paymentUrl = getPaymentUrl(productName, productInfo[1], encryptedBarcode + "&" + email)
        except Exception as e:
            return JsonResponse({"error": f"Failed to generate payment URL: {e}"}, status=500)

        return JsonResponse({"paymentUrl": paymentUrl}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def payByCounterTest(request):
    """
    等待10秒後生成一個兌換網址，並檢查 transactionId 是否已存在於 transactionIdRecord.json 中。
    如果已存在則重新生成，否則記錄並返回兌換網址。

    Args:
        request (HttpRequest): 前端傳來的請求，包含 product, group, 和 email 的 JSON 資料。

    Returns:
        JsonResponse or HttpResponseRedirect: 包含兌換網址或錯誤訊息。
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        data = json.loads(request.body.decode("utf-8"))
        productName = data.get("product", "")
        groupName = data.get("group", "")
        email = data.get("email", "")
        barcode = data.get("barcode", "").split("/")[-1].split(".")[0]
        # 模擬等待 10 秒
        time.sleep(3)

        # 生成 transactionId
        while True:
            current_time = datetime.now().strftime("%Y%m%d")
            random_part = str(random.randint(10000000000, 99999999999))
            transactionId = f"{current_time}{random_part}"

            # 檢查 transactionId 是否已存在
            transactionIdRecordPath = os.path.join(settings.BASE_DIR, "appcoffee", "data", "transactionIdRecord.json")
            with open(transactionIdRecordPath, "r", encoding="utf-8") as file:
                transactionData = json.load(file)

            if transactionId not in transactionData.get("transctionid", []):
                # 如果不存在，記錄並退出循環
                transactionData["transctionid"].append(transactionId)
                with open(transactionIdRecordPath, "w", encoding="utf-8") as file:
                    json.dump(transactionData, file, ensure_ascii=False, indent=4)
                break
        stock = search_product_by_orderid(barcode)[0]["quentity"]
        insert_transaction((transactionId, barcode, stock, email, 1))
        # 回傳兌換網址
        orderId = f"{encrypt(barcode, ENCRYPT_KEY)}"
        redirectUrl = f"http://127.0.0.1:8000/exchange/?transaction={transactionId}&orderId={orderId}&email={email}"
        # redirectUrl = f"https://savegift.dpdns.org//exchange/?transaction={transactionId}&orderId={orderId}&email={email}"
        send_exchange_link = send_email(redirectUrl, email)
        return JsonResponse({"url": redirectUrl}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print(f"發生錯誤: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def payByCounter(request):
    """處理臨櫃付款的請求，回傳對應商品的條碼。

    從 POST 請求中提取 group 與 product 資訊，解析產品名稱，  
    並從本地 JSON 檔案中讀取對應商品的條碼欄位，返回給前端顯示。

    Args:
        request (HttpRequest): 前端傳來的 POST 請求，包含 group 和 product 的 JSON。

    Returns:
        JsonResponse: 成功時回傳條碼字串，失敗時回傳錯誤訊息與 HTTP 狀態碼。
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        data = json.loads(request.body.decode("utf-8"))
        groupName = data.get("group", "")
        productName = data.get("product", "")
        print(groupName, productName)

        jsonPath = os.path.join(settings.BASE_DIR, "appcoffee", "data", "productInfo.json")
        with open(jsonPath, "r", encoding="utf-8") as file:
            jsonData = json.load(file)

        productInfo = jsonData.get(groupName, {}).get(productName)

        if not productInfo:
            return JsonResponse({"error": "Product not found"}, status=404)
        barcode = productInfo[5]
        return JsonResponse({"barcode": barcode}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def confirmTransactionID(request):
    """
    ##0418##
    檢查使用者提供的交易 URL 是否已經完成付款，通過比對transition Id 和 orderId。
    Args:
        request (HttpRequest): 包含 transactionID 參數的 POST 請求
            - 如果確認付款則導致兌換頁面
    Returns:
        JsonResponse: 回傳是否資料庫已有該筆交易紀錄。
    """
    if request.method == "POST":
        try:
            if not request.body:
                return JsonResponse({"error": "Empty request body"}, status=400)

            data = json.loads(request.body.decode("utf-8"))
            clientTransactionId = data.get("transactionID", "")
            print(clientTransactionId)
            encryptedOrderId = data.get("orderId")
            email = data.get("email")
            print(data)
            try:
                originalOrorderId = encryptedOrderId.strip().replace(" ", "+")
                decryptedOrderId = decrypt(originalOrorderId, ENCRYPT_KEY)
                print(f"解密 orderId: {decryptedOrderId}")
            except Exception as e:
                print(f"解密失敗: {e}")
                return JsonResponse({"error": "Failed to decrypt orderId"}, status=400)
            
            if search_transaction(clientTransactionId) and search_orderid(decryptedOrderId):
                # http://127.0.0.1:8000/exchange/?transaction=2025051743523818130&orderId=zTUU5giUDsvG8nHA9i6pnQ==:5YVgWd3p2siuJ3HFfnEJZg==&email=yenchichi95706@gmail.com
                exchange_link = f'exchangelink: https://https://savegift.dpdns.org/exchange/?transaction={clientTransactionId}&orderId={originalOrorderId}&email={email}'
                print(exchange_link)
                return JsonResponse({"success": True}, status=200)
            else:
                return JsonResponse({"success": False}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            print(f"發生錯誤: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def linePayConfirmTransactionID(request):
    """
    處理用戶付款完成後的請求，寫入交易資訊至資料庫。

    ###
    0426
    將網址傳送至user email
    ###
    
    Args:
        request (HttpRequest): 前端 LINE Pay 回傳的 GET 請求，包含 transactionId 與加密 orderId。

    Returns:
        HttpResponseRedirect or JsonResponse:
            - 成功時將使用者重導至首頁，並附上 transactionId 與 orderId。
            - 若缺少必要參數則回傳錯誤訊息。
    """
    transactionId = request.GET.get("transactionId")
    orderId = request.GET.get("orderId")

    if not transactionId or not orderId:
        return JsonResponse({"error": "Missing transactionId or orderId"}, status=400)

    try:
        decryptedOrderId = decrypt(orderId, ENCRYPT_KEY)
        print(f"transactionId: {transactionId}")
        print(f"orderId: {orderId}")
        print(f"解密後的 orderId: {decryptedOrderId}")
        email = orderId.split("&")[1]
        # 更新交易紀錄檔案
        productJsonPath = os.path.join(settings.BASE_DIR, "appcoffee", "data", "productInfo.json")
        transactionIdRecordPath = os.path.join(settings.BASE_DIR, "appcoffee", "data", "transactionIdRecord.json")

        with open(productJsonPath, "r", encoding="utf-8") as productFile:
            productinfo = json.load(productFile)
        
        with open(transactionIdRecordPath, "r", encoding="utf-8") as idtFile:
            transactiorecordnData = json.load(idtFile)

        quentity = -1
        for category, items in productinfo.items():
            for name, values in items.items():
                if values[5] == decryptedOrderId:
                    quentity = values[0]
        insert_transaction((transactionId, decryptedOrderId, quentity, email, 1))
        transactiorecordnData["transctionid"].append(transactionId)
        with open(transactionIdRecordPath, "w", encoding="utf-8") as files:
            json.dump(transactiorecordnData, files, ensure_ascii=False, indent=4)
        
        redirectUrl = f"http://127.0.0.1:8000/?transaction={transactionId}&orderId={orderId}&email={email}"
        # redirectUrl = f"https://savegift.dpdns.org/?transaction={transactionId}&orderId={orderId}&email={email}"
        # 發送電子郵件給用戶
        send_email(redirectUrl, email)
        return redirect(redirectUrl)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def send_email(redirectUrl, email):
    """
    發送具有設計感的電子郵件給用戶，包含兌換網址。

    Args:
        redirectUrl (str): 兌換網址。
        email (str): 收件者的 Email。

    Returns:
        str: 成功或失敗的訊息。
    """
    try:
        subject = "🎁 您的兌換網址來囉！"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # HTML 內容
        html_content = render_to_string("email_template.html", {
            "redirect_url": redirectUrl
        })

        # 純文字內容（作為備用）
        text_content = f"請點擊以下連結進行兌換：\n{redirectUrl}"

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {e}"
'''
0501代辦事項
1. 完成兌換頁面
'''