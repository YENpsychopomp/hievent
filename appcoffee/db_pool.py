from dbutils.pooled_db import PooledDB
import mysql.connector

pool = PooledDB(
    creator=mysql.connector,
    maxconnections=10,
    mincached=2,
    maxcached=5,
    blocking=True,
    ping=1,  # 每次取用連線前檢查是否還活著
    host='127.0.0.1',
    port=3306,
    user='chichi',
    password='Psychopompcm8e9bct0706',
    database='hilifegift',
    charset='utf8mb4'
)