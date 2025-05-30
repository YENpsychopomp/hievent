from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# 生成隨機salt
def generate_salt():
    return os.urandom(16)  # 生成16字節的隨機數（salt）

# 使用 AES 加密
def encrypt(num, key):
    # 生成隨機 salt
    salt = generate_salt()
    
    # 把數字轉換為字串並填充至16位（AES塊大小）
    data = str(num).encode('utf-8')
    data = pad(data, AES.block_size)  # 使用填充來保證數據長度是 AES 的塊大小
    
    # 使用 AES 加密
    cipher = AES.new(key, AES.MODE_CBC, salt)
    encrypted = cipher.encrypt(data)
    
    # 返回加密的字串，並把 salt 和密文合併並 Base64 編碼
    encrypted_data = base64.b64encode(encrypted).decode('utf-8')
    salt_base64 = base64.b64encode(salt).decode('utf-8')
    
    # 將密文和 salt 一起封裝在 num 中返回
    return f"{salt_base64}:{encrypted_data}"

# 使用 AES 解密
def decrypt(num, key):
    # 分離 salt 和加密的數據
    salt_base64, encrypted_data = num.split(":")
    
    # 解碼 salt 和密文
    salt = base64.b64decode(salt_base64)
    encrypted_data = base64.b64decode(encrypted_data)
    
    # 使用相同的 salt 解密
    cipher = AES.new(key, AES.MODE_CBC, salt)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    
    # 返回解密後的原始數字
    return decrypted.decode('utf-8').strip()

# 測試
if __name__ == "__main__":
    key = b'9364009534950706'  # 固定的16字節密鑰
    
    original_number = 8602009988892  # 測試數字
    print(f"原始數字: {original_number}")
    for i in range(5):
        encrypted_with_salt = encrypt(original_number, key)
        decrypted = decrypt(encrypted_with_salt, key)
        print(f"[{i+1}] 加密後: {encrypted_with_salt}, 解密還原: {decrypted}")