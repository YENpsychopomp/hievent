from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime
from .linePayHelper import getPaymentUrl
from .encryption import *
from .operationDatabase import *
import io
from django.http import HttpResponse
from barcode import Code128
from barcode.writer import ImageWriter

import json
import os
import re
import random

ENCRYPT_KEY = b'9364009534950706'

def index(request):
    return render(request, 'exchange.html', {
        'title':"萊爾富 | 來送禮 | 兌換頁面",
        'data':"Version: 0.1.0",
        'now':datetime.now()
    } )

def getProductInfo(request):
    """取得產品資訊的 API。

    此函式處理 POST 請求，解析請求中的 JSON 資料，並根據提供的交易 ID 和訂單 ID
    查詢相關的產品資訊與庫存數量。

    Args:
        request: Django 的 HttpRequest 物件，包含請求的相關資訊。

    Returns:
        JsonResponse: 包含產品資訊的 JSON 回應，或錯誤訊息與對應的 HTTP 狀態碼。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            transactionId = data.get('transactionId')
            orderId = data.get('orderId').replace(" ", "+")
            decryptedOrderId = decrypt(orderId, ENCRYPT_KEY)
            if not decryptedOrderId:
                return JsonResponse({'error': 'Invalid order ID.'}, status=400)
            # 查詢資料庫以獲取產品資訊
            productInfo = search_product_by_orderid(decryptedOrderId)
            stock = get_stock_by_transaction_id(transactionId)
            productInfo[0]["quentity"] = stock
            if not productInfo:
                return JsonResponse({'error': 'Transaction ID not found.'}, status=404)

            return JsonResponse({'productInfo': productInfo}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def confirmExchange(request):
    """確認兌換的 API。

    此函式處理 POST 請求，解析請求中的 JSON 資料，並根據提供的交易 ID 和訂單 ID
    確認兌換的相關資訊。

    Args:
        request: Django 的 HttpRequest 物件，包含請求的相關資訊。

    Returns:
        JsonResponse: 包含兌換確認結果的 JSON 回應，或錯誤訊息與對應的 HTTP 狀態碼。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            transactionId = data.get('transactionId')
            if not transactionId:
                return JsonResponse({'error': 'Transaction ID is required.'}, status=400)
            
            if not search_transaction(transactionId):
                return JsonResponse({'success': 'false'}, status=404)
            
            return JsonResponse({'success': 'true'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
def share(request):
    """分享兌換的 API。

    此函式處理 POST 請求，解析請求中的 JSON 資料，並根據提供的交易 ID 和訂單 ID
    確認兌換的相關資訊。

    Args:
        request: Django 的 HttpRequest 物件，包含請求的相關資訊。

    Returns:
        JsonResponse: 包含兌換確認結果的 JSON 回應，或錯誤訊息與對應的 HTTP 狀態碼。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            transactionId = data.get('transactionId')
            encryptedOrderId = data.get('orderId').replace(" ", "+")
            originalOrorderId = encryptedOrderId.strip().replace(" ", "+")
            decryptedOrderId = decrypt(originalOrorderId, ENCRYPT_KEY)
            if not decryptedOrderId:
                return JsonResponse({'error': 'Invalid order ID.'}, status=400)

            if not transactionId:
                return JsonResponse({'error': 'Transaction ID is required.'}, status=400)
            
            if not search_transaction(transactionId):
                return JsonResponse({'success': 'false'}, status=404)
            
            sender = data.get('sender')
            receiver = data.get('receiver')
            amount = data.get('amount')
            mes = data.get('message')
            stock = get_stock_by_transaction_id(transactionId)
            
            if not stock:
                return JsonResponse({'error': 'Stock not found.'}, status=404)
            if stock <= 0:
                return JsonResponse({'error': 'No stock available.'}, status=404)
            if not sender or not receiver or not amount or not mes or stock < int(amount):
                return JsonResponse({'error': 'Sender, receiver, amount, and message are required.'}, status=400)
            if not re.match(r'^[0-9]+$', amount):
                return JsonResponse({'error': 'Amount must be a number.'}, status=400)
            
            sharelinkRandom = random.randint(1000000000000, 9999999999999)
            path = f"shares/?orderId={encrypt(decryptedOrderId, ENCRYPT_KEY)}&sharelink={encrypt(sharelinkRandom, ENCRYPT_KEY)}"
            insert_shares((sender, receiver, mes, path, int(amount), decryptedOrderId))
            updatate_stock(transactionId, stock - int(amount))
            return JsonResponse({
                'success': 'true',
                # 'url': f"https://savegift.dpdns.org/exchange/{path}",
                'url': f"https://127.0.0.1:8000/exchange/{path}",
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def shares(request):
    return render(request, 'share.html', {
        'title':"萊爾富 | 來送禮 | 兌換頁面",
        'data':"Version: 0.1.0",
        'now':datetime.now()
    } )

def sharesInit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            url = data.get('url')
            match = re.search(r"shares/.*", url)
            
            if match:
                clientPath = match.group(0)
            else:
                print("找不到指定的 URL 部分。")
            
            shareInfo = get_shares_by_path(clientPath)
            encrypted = decrypt(re.search(r"&sharelink=.*", url).group(0).split('&sharelink=')[1], ENCRYPT_KEY)
            return JsonResponse({'status': "success", "stock": shareInfo[0].get("stock"), "code1": encrypted}, status=200)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        
def transactionBarcode(request, code):
    """生成交易條碼的視圖函式。

    Args:
        request: Django 的 HttpRequest 物件，包含請求的相關資訊。
        code: 條碼的代碼。

    Returns:
        HttpResponse: 包含條碼圖片的回應。
    """
    try:
        buffer = io.BytesIO()
        barcode = Code128(code, writer=ImageWriter())
        barcode.write(buffer)
        return HttpResponse(buffer.getvalue(), content_type="image/png")
    except Exception as e:
        return HttpResponse(f"錯誤：{e}", status=400)
