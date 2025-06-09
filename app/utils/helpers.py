# 引入string模組，用於獲取字母和數字字符集
import string
# 引入random模組，用於生成隨機字符
import random
# 引入bcrypt模組，用於密碼加密和驗證
import bcrypt
# 引入Flask的request物件，用於獲取HTTP請求的相關信息
from flask import request

def generate_short_code(length=6):
    """生成隨機短網址代碼
    
    透過隨機選擇字母和數字的組合，生成指定長度的短網址代碼。
    
    參數:
        length (int): 短網址代碼的長度，預設為6個字符
        
    返回:
        str: 生成的隨機短網址代碼
    """
    # 定義可用字符集，包含所有大小寫字母和數字
    characters = string.ascii_letters + string.digits
    # 從字符集中隨機選擇指定數量的字符，並組合為一個字符串
    return ''.join(random.choice(characters) for _ in range(length))

def hash_password(password):
    """密碼雜湊
    
    使用bcrypt算法對密碼進行安全的雜湊處理，
    生成的雜湊值包含了隨機鹽值，增強安全性。
    
    參數:
        password (str): 要加密的明文密碼
        
    返回:
        str: 雜湊後的密碼字符串
    """
    # 將密碼轉換為 bytes 類型，bcrypt只接受bytes類型的輸入
    password_bytes = password.encode('utf-8')
    # 生成隨機鹽值，增強密碼安全性，防止彩虹表攻擊
    salt = bcrypt.gensalt()
    # 使用生成的鹽值對密碼進行雜湊處理
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 將bytes類型的雜湊結果轉換為字符串並返回
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    """驗證密碼
    
    檢查明文密碼是否與已雜湊的密碼匹配。
    bcrypt會自動從雜湊密碼中提取鹽值，並用相同鹽值
    對輸入的明文密碼進行雜湊，然後比較結果。
    
    參數:
        password (str): 要驗證的明文密碼
        hashed_password (str): 已雜湊的密碼
        
    返回:
        bool: 如果密碼匹配則返回True，否則返回False
    """
    # 將明文密碼轉換為bytes類型
    password_bytes = password.encode('utf-8')
    # 將雜湊密碼轉換為bytes類型
    hashed_bytes = hashed_password.encode('utf-8')
    # 使用bcrypt的checkpw函數檢查密碼是否匹配
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_client_info():
    """獲取客戶端資訊
    
    從當前HTTP請求中提取客戶端的相關信息，
    包括IP地址、瀏覽器用戶代理和來源頁面。
    用於記錄短網址的訪問日誌。
    
    返回:
        dict: 包含客戶端信息的字典，包括:
            - ip_address: 訪問者的IP地址
            - user_agent: 訪問者的瀏覽器和操作系統信息
            - referer: 訪問者來源頁面URL
    """
    return {
        # 獲取訪問者的IP地址
        'ip_address': request.remote_addr,
        # 獲取訪問者的瀏覽器和操作系統信息，若無則設為None
        'user_agent': request.user_agent.string if request.user_agent else None,
        # 獲取訪問者的來源頁面URL
        'referer': request.referrer
    }
