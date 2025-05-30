import uuid
import json
import hashlib
import hmac
import base64
import requests

LINE_PAY_KEY = "d8aa26a82caa3ce2b9da1a1fb7011a34"
LINE_PAY_URI = "/v3/payments/request"
LINE_CHANNEL_ID = 2006589457
LINE_PAY_URL = "https://sandbox-api-pay.line.me" + LINE_PAY_URI

def getPaymentUrl(product_name, amount, orderId):
    nonce = str(uuid.uuid4())
    body = {
        "amount": amount,
        "currency": "TWD",
        "orderId": orderId,
        "packages": [
            {
                "id": orderId,
                "amount": amount,
                "products": [
                    {
                        "id": orderId,
                        "name": product_name,
                        "quantity": 1,
                        "price": amount
                    }
                ]
            }
        ],
        "redirectUrls": {
            "confirmUrl": "http://127.0.0.1:8000/linePayConfirmTransactionID/",
            "cancelUrl": "http://127.0.0.1:8000"
        }
        # "confirmUrl": "https://savegift.dpdns.org//linePayConfirmTransactionID/",
        # "cancelUrl": "https://savegift.dpdns.org/"
    }

    # Generate HMAC signature
    message = LINE_PAY_KEY + LINE_PAY_URI + json.dumps(body) + nonce
    hmac_signature = hmac.new(LINE_PAY_KEY.encode(), message.encode(), hashlib.sha256).digest()

    hmac_base64 = base64.b64encode(hmac_signature).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'X-LINE-ChannelId': str(LINE_CHANNEL_ID),
        'X-LINE-Authorization-Nonce': nonce,
        'X-LINE-Authorization': hmac_base64
    }

    response = requests.post(LINE_PAY_URL, json=body, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('info', {}).get('paymentUrl', {}).get('web')
    else:
        raise Exception("LINE Pay request failed: " + response.text)

if __name__ == "__main__":
    getPaymentUrl("abc", 9999)