# 短網址服務 API

這是一個使用 Flask 和 SQLite 開發的短網址服務後端 API。

## 功能特點

- **多使用者系統**
  - 使用者註冊、登入、個人資料管理
  - 基於 JWT 的身分驗證和授權
  - 使用者角色管理（普通使用者和管理員）

- **短網址管理**
  - 創建自定義短網址
  - 管理短網址（更新、刪除、啟用/停用）
  - 設定短網址過期時間

- **統計分析**
  - 記錄短網址訪問次數
  - 收集訪問 IP、時間、來源等資訊
  - 數據可視化和分析

- **超級管理員功能**
  - 管理所有使用者
  - 管理所有短網址
  - 系統數據統計

## 技術棧

- **後端**: Flask
- **資料庫**: SQLite
- **驗證**: JWT (JSON Web Tokens)
- **密碼安全**: bcrypt 加密

## API 端點

### 身份驗證

- `POST /api/auth/register` - 使用者註冊
- `POST /api/auth/login` - 使用者登入
- `GET /api/auth/profile` - 獲取使用者資料
- `PUT /api/auth/profile` - 更新使用者資料

### 短網址管理

- `POST /api/urls/` - 創建短網址
- `GET /api/urls/` - 獲取使用者的短網址列表
- `GET /api/urls/<id>` - 獲取特定短網址詳情
- `PUT /api/urls/<id>` - 更新短網址
- `DELETE /api/urls/<id>` - 刪除短網址
- `GET /s/<short_code>` - 短網址跳轉

### 管理員功能

- `GET /api/admin/users` - 獲取所有使用者列表
- `GET /api/admin/users/<id>` - 獲取特定使用者詳情
- `PUT /api/admin/users/<id>` - 更新使用者
- `DELETE /api/admin/users/<id>` - 刪除使用者
- `GET /api/admin/stats` - 獲取系統統計資料

## 安裝和運行

1. 克隆儲存庫

```bash
git clone <repository-url>
cd shorturl
```

2. 安裝依賴

```bash
uv sync
```

3. 配置環境變數

編輯 `.env` 文件，設定必要的環境變數。

4. 運行應用程式

```bash
uv run main.py
```

5. 訪問 API

API 將在 http://localhost:5000 運行。

## 預設管理員帳號

- 使用者名稱: admin
- 密碼: admin123

## 授權和貢獻

© 2025 版權所有