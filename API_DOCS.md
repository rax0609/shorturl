# 短網址服務 API 文件

本文件詳細說明了短網址服務的所有 API 端點、請求參數和返回內容。

## 目錄

- [身份驗證 API](#身份驗證-api)
  - [註冊新用戶](#註冊新用戶)
  - [用戶登入](#用戶登入)
  - [獲取個人資料](#獲取個人資料)
  - [更新個人資料](#更新個人資料)
- [短網址 API](#短網址-api)
  - [創建短網址](#創建短網址)
  - [獲取短網址列表](#獲取短網址列表)
  - [獲取短網址詳情](#獲取短網址詳情)
  - [更新短網址](#更新短網址)
  - [刪除短網址](#刪除短網址)
  - [短網址跳轉](#短網址跳轉)
- [管理員 API](#管理員-api)
  - [獲取所有用戶](#獲取所有用戶)
  - [獲取特定用戶詳情](#獲取特定用戶詳情)
  - [更新用戶資料](#更新用戶資料)
  - [刪除用戶](#刪除用戶)
  - [獲取系統統計資料](#獲取系統統計資料)

## 身份驗證 API

### 註冊新用戶

**請求方法:** `POST`

**URL:** `/api/auth/register`

**請求體:**
```json
{
  "username": "testuser",  // 必須，用戶名，字串
  "password": "password123",  // 必須，密碼，字串
  "email": "test@example.com"  // 必須，電子郵件，字串
}
```

**成功回應:** (HTTP 狀態碼: 201)
```json
{
  "message": "註冊成功",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

**失敗回應:**

- 缺少必要欄位 (HTTP 狀態碼: 400)
```json
{
  "message": "缺少必要欄位"
}
```

- 用戶名已存在 (HTTP 狀態碼: 409)
```json
{
  "message": "使用者名稱已存在"
}
```

- 電子郵件已存在 (HTTP 狀態碼: 409)
```json
{
  "message": "電子郵件已存在"
}
```

### 用戶登入

**請求方法:** `POST`

**URL:** `/api/auth/login`

**請求體:**
```json
{
  "username": "testuser",  // 必須，用戶名，字串
  "password": "password123"  // 必須，密碼，字串
}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "登入成功",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

**失敗回應:**

- 缺少必要欄位 (HTTP 狀態碼: 400)
```json
{
  "message": "缺少使用者名稱或密碼"
}
```

- 認證失敗 (HTTP 狀態碼: 401)
```json
{
  "message": "使用者名稱或密碼錯誤"
}
```

- 帳戶已停用 (HTTP 狀態碼: 403)
```json
{
  "message": "帳號已被停用"
}
```

### 獲取個人資料

**請求方法:** `GET`

**URL:** `/api/auth/profile`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "created_at": "2025-06-01T10:00:00.000000",
    "updated_at": "2025-06-01T10:00:00.000000"
  }
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 用戶不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "使用者不存在"
}
```

- 帳戶已停用 (HTTP 狀態碼: 403)
```json
{
  "message": "帳號已被停用"
}
```

### 更新個人資料

**請求方法:** `PUT`

**URL:** `/api/auth/profile`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**請求體:** (可選欄位)
```json
{
  "email": "newemail@example.com",  // 選填，新電子郵件
  "current_password": "password123",  // 更改密碼時必填，當前密碼
  "new_password": "newpassword123"  // 更改密碼時必填，新密碼
}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "資料更新成功"
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 電子郵件已被使用 (HTTP 狀態碼: 409)
```json
{
  "message": "電子郵件已被使用"
}
```

- 當前密碼錯誤 (HTTP 狀態碼: 401)
```json
{
  "message": "目前密碼錯誤"
}
```

## 短網址 API

### 創建短網址

**請求方法:** `POST`

**URL:** `/api/urls/`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**請求體:**
```json
{
  "original_url": "https://www.example.com",  // 必須，原始網址
  "title": "Example Website",  // 選填，短網址標題
  "expires_days": 30  // 選填，過期天數，整數
}
```

**成功回應:** (HTTP 狀態碼: 201)
```json
{
  "message": "短網址建立成功",
  "url": {
    "id": 1,
    "original_url": "https://www.example.com",
    "short_code": "a1b2c3",
    "short_url": "http://localhost:5000/s/a1b2c3",
    "title": "Example Website",
    "created_at": "2025-06-01T10:00:00.000000",
    "expires_at": "2025-07-01T10:00:00.000000",
    "is_active": true
  }
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 缺少必要欄位 (HTTP 狀態碼: 400)
```json
{
  "message": "缺少原始網址"
}
```

### 獲取短網址列表

**請求方法:** `GET`

**URL:** `/api/urls/`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**查詢參數:**
- `page`: 頁碼，默認為 1
- `per_page`: 每頁項目數，默認為 10
- `is_active`: 篩選狀態 (true/false)
- `search`: 搜尋關鍵字

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "urls": [
    {
      "id": 1,
      "original_url": "https://www.example.com",
      "short_code": "a1b2c3",
      "short_url": "http://localhost:5000/s/a1b2c3",
      "title": "Example Website",
      "created_at": "2025-06-01T10:00:00.000000",
      "expires_at": "2025-07-01T10:00:00.000000",
      "is_active": true,
      "visit_count": 5
    },
    {
      "id": 2,
      "original_url": "https://www.google.com",
      "short_code": "d4e5f6",
      "short_url": "http://localhost:5000/s/d4e5f6",
      "title": "Google",
      "created_at": "2025-06-01T09:00:00.000000",
      "expires_at": null,
      "is_active": true,
      "visit_count": 10
    }
  ],
  "total": 2,
  "pages": 1,
  "page": 1,
  "per_page": 10
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

### 獲取短網址詳情

**請求方法:** `GET`

**URL:** `/api/urls/{url_id}`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "url": {
    "id": 1,
    "original_url": "https://www.example.com",
    "short_code": "a1b2c3",
    "short_url": "http://localhost:5000/s/a1b2c3",
    "title": "Example Website",
    "created_at": "2025-06-01T10:00:00.000000",
    "updated_at": "2025-06-01T10:00:00.000000",
    "expires_at": "2025-07-01T10:00:00.000000",
    "is_active": true,
    "visit_count": 5
  },
  "visits": [
    {
      "id": 1,
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
      "referer": "https://www.google.com",
      "timestamp": "2025-06-01T12:00:00.000000"
    },
    {
      "id": 2,
      "ip_address": "192.168.1.2",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
      "referer": null,
      "timestamp": "2025-06-01T13:00:00.000000"
    }
  ]
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 短網址不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "短網址不存在"
}
```

- 無權訪問 (HTTP 狀態碼: 403)
```json
{
  "message": "無權訪問"
}
```

### 更新短網址

**請求方法:** `PUT`

**URL:** `/api/urls/{url_id}`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**請求體:** (至少包含一個欄位)
```json
{
  "title": "Updated Example Website",  // 選填，更新標題
  "original_url": "https://www.example.org",  // 選填，更新原始網址
  "is_active": false,  // 選填，更新狀態
  "expires_days": 60  // 選填，更新過期天數
}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "短網址更新成功",
  "url": {
    "id": 1,
    "original_url": "https://www.example.org",
    "short_code": "a1b2c3",
    "short_url": "http://localhost:5000/s/a1b2c3",
    "title": "Updated Example Website",
    "created_at": "2025-06-01T10:00:00.000000",
    "updated_at": "2025-06-01T11:00:00.000000",
    "expires_at": "2025-08-01T10:00:00.000000",
    "is_active": false
  }
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 短網址不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "短網址不存在"
}
```

- 無權更新 (HTTP 狀態碼: 403)
```json
{
  "message": "無權更新"
}
```

### 刪除短網址

**請求方法:** `DELETE`

**URL:** `/api/urls/{url_id}`

**請求頭:**
```
Authorization: Bearer {access_token}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "短網址刪除成功"
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 短網址不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "短網址不存在"
}
```

- 無權刪除 (HTTP 狀態碼: 403)
```json
{
  "message": "無權刪除"
}
```

### 短網址跳轉

**請求方法:** `GET`

**URL:** `/s/{short_code}`

**成功回應:** 
- HTTP 狀態碼: 302 Found
- 跳轉到原始網址

**失敗回應:**

- 短網址不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "短網址不存在"
}
```

- 短網址已停用 (HTTP 狀態碼: 403)
```json
{
  "message": "此短網址已被停用"
}
```

- 短網址已過期 (HTTP 狀態碼: 403)
```json
{
  "message": "此短網址已過期"
}
```

## 管理員 API

### 獲取所有用戶

**請求方法:** `GET`

**URL:** `/api/admin/users`

**請求頭:**
```
Authorization: Bearer {access_token}  // 必須是管理員 token
```

**查詢參數:**
- `page`: 頁碼，默認為 1
- `per_page`: 每頁項目數，默認為 10
- `search`: 搜尋關鍵字
- `role`: 按角色篩選 (user/admin)
- `is_active`: 按狀態篩選 (true/false)

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-06-01T08:00:00.000000",
      "updated_at": "2025-06-01T08:00:00.000000",
      "url_count": 0
    },
    {
      "id": 2,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "is_active": true,
      "created_at": "2025-06-01T09:00:00.000000",
      "updated_at": "2025-06-01T09:00:00.000000",
      "url_count": 2
    }
  ],
  "total": 2,
  "pages": 1,
  "page": 1,
  "per_page": 10
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 權限不足 (HTTP 狀態碼: 403)
```json
{
  "message": "需要管理員權限"
}
```

### 獲取特定用戶詳情

**請求方法:** `GET`

**URL:** `/api/admin/users/{user_id}`

**請求頭:**
```
Authorization: Bearer {access_token}  // 必須是管理員 token
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-06-01T09:00:00.000000",
    "updated_at": "2025-06-01T09:00:00.000000"
  },
  "urls": [
    {
      "id": 1,
      "original_url": "https://www.example.com",
      "short_code": "a1b2c3",
      "title": "Example Website",
      "created_at": "2025-06-01T10:00:00.000000",
      "is_active": true,
      "visit_count": 5
    },
    {
      "id": 2,
      "original_url": "https://www.google.com",
      "short_code": "d4e5f6",
      "title": "Google",
      "created_at": "2025-06-01T11:00:00.000000",
      "is_active": true,
      "visit_count": 10
    }
  ]
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 權限不足 (HTTP 狀態碼: 403)
```json
{
  "message": "需要管理員權限"
}
```

- 用戶不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "使用者不存在"
}
```

### 更新用戶資料

**請求方法:** `PUT`

**URL:** `/api/admin/users/{user_id}`

**請求頭:**
```
Authorization: Bearer {access_token}  // 必須是管理員 token
```

**請求體:** (至少包含一個欄位)
```json
{
  "email": "newemail@example.com",  // 選填，更新電子郵件
  "role": "admin",  // 選填，更新角色 (user/admin)
  "is_active": false,  // 選填，更新狀態
  "reset_password": true,  // 選填，是否重設密碼
  "new_password": "newpassword123"  // 選填，新密碼 (與 reset_password 一起使用)
}
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "使用者資料更新成功",
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "newemail@example.com",
    "role": "admin",
    "is_active": false
  }
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 權限不足 (HTTP 狀態碼: 403)
```json
{
  "message": "需要管理員權限"
}
```

- 用戶不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "使用者不存在"
}
```

- 電子郵件已被使用 (HTTP 狀態碼: 409)
```json
{
  "message": "電子郵件已被使用"
}
```

- 無效的角色值 (HTTP 狀態碼: 400)
```json
{
  "message": "無效的角色值"
}
```

### 刪除用戶

**請求方法:** `DELETE`

**URL:** `/api/admin/users/{user_id}`

**請求頭:**
```
Authorization: Bearer {access_token}  // 必須是管理員 token
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "message": "使用者刪除成功"
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 權限不足 (HTTP 狀態碼: 403)
```json
{
  "message": "需要管理員權限"
}
```

- 用戶不存在 (HTTP 狀態碼: 404)
```json
{
  "message": "使用者不存在"
}
```

- 無法刪除當前用戶 (HTTP 狀態碼: 403)
```json
{
  "message": "無法刪除當前使用者"
}
```

### 獲取系統統計資料

**請求方法:** `GET`

**URL:** `/api/admin/stats`

**請求頭:**
```
Authorization: Bearer {access_token}  // 必須是管理員 token
```

**成功回應:** (HTTP 狀態碼: 200)
```json
{
  "users": {
    "total": 5,
    "active": 4
  },
  "urls": {
    "total": 20,
    "active": 18
  },
  "visits": {
    "total": 150,
    "daily": [
      {"date": "2025-05-26", "count": 15},
      {"date": "2025-05-27", "count": 22},
      {"date": "2025-05-28", "count": 18},
      {"date": "2025-05-29", "count": 25},
      {"date": "2025-05-30", "count": 20},
      {"date": "2025-05-31", "count": 30},
      {"date": "2025-06-01", "count": 20}
    ]
  },
  "top_urls": [
    {
      "id": 5,
      "short_code": "g7h8i9",
      "original_url": "https://www.youtube.com",
      "title": "YouTube",
      "visit_count": 35
    },
    {
      "id": 8,
      "short_code": "j0k1l2",
      "original_url": "https://www.github.com",
      "title": "GitHub",
      "visit_count": 28
    }
  ]
}
```

**失敗回應:**

- 未認證 (HTTP 狀態碼: 401)
```json
{
  "msg": "Missing Authorization Header"
}
```

- 權限不足 (HTTP 狀態碼: 403)
```json
{
  "message": "需要管理員權限"
}
```
