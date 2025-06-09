import requests
import json
import time

# API 基本 URL
BASE_URL = 'http://localhost:5000'

# 保存 API 回應
def save_response(title, response):
    print(f"\n===== {title} =====")
    print(f"狀態碼: {response.status_code}")
    try:
        print(f"回應內容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"回應內容: {response.text}")
    print("=" * (len(title) + 12))
    return response.json() if response.status_code < 400 else None

# 測試註冊
def test_register(username, password, email):
    print(f"\n測試註冊: {username}")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": username,
            "password": password,
            "email": email
        }
    )
    result = save_response("註冊結果", response)
    return result.get('access_token') if result else None

# 測試登入
def test_login(username, password):
    print(f"\n測試登入: {username}")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    result = save_response("登入結果", response)
    return result.get('access_token') if result else None

# 測試獲取個人資料
def test_get_profile(token):
    print("\n測試獲取個人資料")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        f"{BASE_URL}/api/auth/profile",
        headers=headers
    )
    return save_response("個人資料", response)

# 測試創建短網址
def test_create_url(token, original_url, title=None, expires_days=None):
    print(f"\n測試創建短網址: {original_url}")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {"original_url": original_url}
    
    if title:
        data["title"] = title
    
    if expires_days:
        data["expires_days"] = expires_days
    
    response = requests.post(
        f"{BASE_URL}/api/urls/",
        headers=headers,
        json=data
    )
    result = save_response("創建短網址結果", response)
    return result.get('url', {}).get('id') if result else None

# 測試獲取短網址列表
def test_get_urls(token):
    print("\n測試獲取短網址列表")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        f"{BASE_URL}/api/urls/",
        headers=headers
    )
    return save_response("短網址列表", response)

# 測試獲取短網址詳情
def test_get_url_details(token, url_id):
    print(f"\n測試獲取短網址詳情: ID={url_id}")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        f"{BASE_URL}/api/urls/{url_id}",
        headers=headers
    )
    return save_response("短網址詳情", response)

# 測試更新短網址
def test_update_url(token, url_id, title=None, is_active=None):
    print(f"\n測試更新短網址: ID={url_id}")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = {}
    
    if title is not None:
        data["title"] = title
    
    if is_active is not None:
        data["is_active"] = is_active
    
    response = requests.put(
        f"{BASE_URL}/api/urls/{url_id}",
        headers=headers,
        json=data
    )
    return save_response("更新短網址結果", response)

# 測試刪除短網址
def test_delete_url(token, url_id):
    print(f"\n測試刪除短網址: ID={url_id}")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.delete(
        f"{BASE_URL}/api/urls/{url_id}",
        headers=headers
    )
    return save_response("刪除短網址結果", response)

# 測試管理員功能 - 獲取使用者列表
def test_admin_get_users(token):
    print("\n測試管理員功能 - 獲取使用者列表")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers=headers
    )
    return save_response("使用者列表", response)

# 測試管理員功能 - 獲取系統統計資料
def test_admin_get_stats(token):
    print("\n測試管理員功能 - 獲取系統統計資料")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(
        f"{BASE_URL}/api/admin/stats",
        headers=headers
    )
    return save_response("系統統計資料", response)

def run_tests():
    """執行所有測試"""
    
    # 1. 測試管理員登入
    admin_token = test_login("admin", "admin123")
    
    if admin_token:
        # 2. 獲取管理員資料
        test_get_profile(admin_token)
        
        # 3. 測試管理員功能
        test_admin_get_users(admin_token)
        test_admin_get_stats(admin_token)
    
    # 4. 測試註冊新使用者
    user_token = test_register("testuser", "password123", "test@example.com")
    
    if not user_token:
        # 如果註冊失敗，嘗試登入
        user_token = test_login("testuser", "password123")
    
    if user_token:
        # 5. 獲取使用者資料
        test_get_profile(user_token)
        
        # 6. 創建短網址
        url1_id = test_create_url(
            user_token, 
            "https://www.google.com", 
            "Google 首頁", 
            30
        )
        
        url2_id = test_create_url(
            user_token, 
            "https://www.youtube.com", 
            "YouTube", 
            15
        )
        
        # 7. 獲取短網址列表
        test_get_urls(user_token)
        
        if url1_id:
            # 8. 獲取短網址詳情
            test_get_url_details(user_token, url1_id)
            
            # 9. 更新短網址
            test_update_url(user_token, url1_id, "更新的 Google 首頁")
            
            # 10. 重新獲取短網址詳情
            test_get_url_details(user_token, url1_id)
        
        if url2_id:
            # 11. 刪除短網址
            test_delete_url(user_token, url2_id)
            
            # 12. 獲取短網址列表（確認已刪除）
            test_get_urls(user_token)

if __name__ == "__main__":
    run_tests()
