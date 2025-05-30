from mysql.connector import Error
import mysql.connector
from .db_pool import pool

def connect_to_mysql():
    """
    使用連線池建立與 MySQL 資料庫的連線。
    如果連線池無法提供連線，則回退至直接建立連線。
    Returns:
        mysql.connector.connection.MySQLConnection: 如果連線成功，返回 MySQL 連線物件。
        None: 如果無法建立連線，返回 None。
    Raises:
        Exception: 當連線池無法提供連線時拋出。
        mysql.connector.Error: 當無法直接建立 MySQL 連線時拋出。
    """
    try:
        connection = pool.connection()
        if connection.is_connected():
            return connection
    except Exception as pool_error:
        print("連線池無法取得連線，使用單次建立連線，請注意。原因：", pool_error)
    
    # 回退方案：直接建立連線
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='chichi',
            password='Psychopompcm8e9bct0706',
            database='hilifegift'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("無法連接 MySQL：", e)

    return None

def insert_product_info(product_info_tuple):
    """
    將單條產品資訊插入到資料庫的 `productInfo` 表中。
    Args:
        product_info_tuple (tuple): 包含單條產品資訊的元組，格式如下：
            (name, quantity, price, img_path, unit, time, barcode_path, description, product_group)
    Raises:
        Error: 當執行 SQL 插入操作時發生錯誤時拋出。
    注意:
        - 此函式會在插入資料後自動提交變更。
        - 若發生錯誤，會印出錯誤訊息並確保游標被正確關閉。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = """
        INSERT INTO product (name, quantity, price, img_path, unit, time, barcode_path, description, product_group)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, product_info_tuple)
        connection.commit()
        return "Product information inserted successfully"
    except Error as e:
        return f"Error while inserting data into MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def insert_transaction(transaction_info_tuple):
    """
    將單條交易資訊插入到資料庫的 `transaction` 表中。
    Args:
        transaction_info_tuple (tuple): 包含單條交易資訊的元組，格式如下：
            (transaction_id, product_id, stock, email, payment_status)
    Raises: 
        Error: 當執行 SQL 插入操作時發生錯誤時拋出。
    注意:
        - 此函式會在插入資料後自動提交變更。
        - 若發生錯誤，會印出錯誤訊息並確保游標被正確關閉。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = """
        INSERT INTO transaction (transactionID, productid, stock, email, payment_stuts)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, transaction_info_tuple)
        connection.commit()
        return "Transaction information inserted successfully"
    except Error as e:
        return f"Error while inserting data into MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def search_transaction(transaction_id):
    """
    查找指定的交易 ID 是否存在於資料庫的 `transaction` 表的 `transactionID` 欄位中
    Args:
        transaction_id (str): 要查找的交易 ID
    Returns:
        bool: 如果 `transactionID` 欄位包含指定的交易 ID，返回 True；否則返回 False。
        str: 如果發生錯誤，返回錯誤訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM transaction WHERE transactionID = %s"
        cursor.execute(sql, (transaction_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def search_orderid(order_id):
    """
    查找指定的訂單 ID 是否存在於資料庫的 `orders` 表的 `orderID` 欄位中
    Args:
        order_id (str): 要查找的訂單 ID
    Returns:
        bool: 如果 `orderID` 欄位包含指定的訂單 ID，返回 True；否則返回 False。
        str: 如果發生錯誤，返回錯誤訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM orders WHERE orderID = %s"
        cursor.execute(sql, (order_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def search_product_by_orderid(order_id):
    """
    根據指定的訂單 ID 查找相關的產品資訊
    Args:
        order_id (str): 要查找的訂單 ID
    Returns:
        list: 包含相關產品資訊的列表，每個元素為一個字典，包含產品的詳細資訊。
        str: 如果發生錯誤，返回錯誤訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor(dictionary=True)
        sql = "SELECT * FROM product WHERE barcode_path = %s"
        cursor.execute(sql, (order_id,))
        result = cursor.fetchall()
        return result if result else f"No products found for order ID {order_id}"
    except Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def get_stock_by_transaction_id(transaction_id):
    """
    根據指定的交易 ID 查找相關的庫存資訊
    Args:
        transaction_id (str): 要查找的交易 ID
    Returns:
        int: 返回庫存數量，如果找到相關交易。
        str: 如果發生錯誤或未找到交易，返回錯誤訊息或提示訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = "SELECT stock FROM transaction WHERE transactionID = %s"
        cursor.execute(sql, (transaction_id,))
        result = cursor.fetchone()
        return result[0] if result else f"No transactions found for transaction ID {transaction_id}"
    except Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def get_product_info_by_group(group):
    """
    根據指定的產品組查找相關的產品資訊
    Args:
        group (str): 要查找的產品組
    Returns:
        list: 包含相關產品資訊的列表，每個元素為一個字典，包含產品的詳細資訊。
        str: 如果發生錯誤，返回錯誤訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"

    try:
        cursor = connection.cursor(dictionary=True)
        sql = "SELECT * FROM product WHERE product_group = %s"
        cursor.execute(sql, (group,))
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        # 用 close() 釋放連線（不論來自 pool 與否皆可呼叫）
        connection.close()

def insert_shares(share_info_tuple):
    """
    將單條分享資訊插入到資料庫的 `share` 表中。
    Args:
        share_info_tuple (tuple): 包含單條分享資訊的元組，格式如下：
            (sender, receiver, message, path, stock)
    Raises:
        Error: 當執行 SQL 插入操作時發生錯誤時拋出。
    注意:
        - 此函式會在插入資料後自動提交變更。
        - 若發生錯誤，會印出錯誤訊息並確保游標被正確關閉。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = """
        INSERT INTO shares (sender, receiver, message, path, stock, productid)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, share_info_tuple)
        connection.commit()
        return "Share information inserted successfully"
    except Error as e:
        return f"Error while inserting data into MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

def get_shares_by_path(path):
    """
    根據指定的訂單 ID 查找相關的分享資訊
    Args:
        order_id (str): 要查找的訂單 ID
    Returns:
        list: 包含相關分享資訊的列表，每個元素為一個字典，包含分享的詳細資訊。
        str: 如果發生錯誤，返回錯誤訊息。
    Raises:
        Error: 當執行 SQL 查詢操作時發生錯誤時拋出。
    """
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor(dictionary=True)
        sql = "SELECT * FROM shares WHERE path = %s"
        cursor.execute(sql, (path,))
        result = cursor.fetchall()
        return result if result else f"No shares found for order ID {path}"
    except Error as e:
        return f"Error while searching data in MySQL {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()
            
def updatate_stock(transactionid, newStock):
    connection = connect_to_mysql()
    if connection is None:
        return "Failed to connect to MySQL"
    try:
        cursor = connection.cursor()
        sql = "UPDATE transaction SET stock = %s WHERE transactionID = %s"

        cursor.execute(sql, (newStock, transactionid))
        connection.commit()  # 必須 commit，否則更新不會生效
        if cursor.rowcount == 0:
            return f"No record found with transactionID = {transactionid}"
        return f"Stock updated to {newStock} for transactionID = {transactionid}"
    except Error as e:
        return f"Error while updating data in MySQL: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='chichi',
            password='Psychopompcm8e9bct0706',
            database='hilifegift'
        )
        if connection.is_connected():
            print("已連接到資料庫!")
            db_info = connection.get_server_info()
            print("MySQL Server version:", db_info)

    except Error as e:
        print("Error while interacting with MySQL", e)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")