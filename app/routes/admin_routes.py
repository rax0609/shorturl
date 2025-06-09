# 引入Flask相關模組，用於處理HTTP請求和回應
from flask import Blueprint, request, jsonify
# 引入JWT相關函數，用於驗證用戶身份
from flask_jwt_extended import jwt_required, get_jwt_identity
# 引入自定義的數據模型類和資料庫物件
from app.models.models import User, URL, URLVisit, UserRole, db
# 引入密碼雜湊的工具函數
from app.utils.helpers import hash_password
# 引入SQLAlchemy的進階查詢函數
from sqlalchemy import desc, func, case
# 引入日期時間相關模組，用於處理時間範圍查詢
from datetime import datetime, timedelta

# 創建一個藍圖(Blueprint)，用於組織管理員相關的路由
admin_bp = Blueprint('admin', __name__)

# 管理員權限驗證裝飾器
def admin_required(fn):
    """檢查是否為管理員的裝飾器"""
    @jwt_required()  # 首先確保用戶已經通過JWT身份驗證
    def wrapper(*args, **kwargs):
        # 獲取當前已驗證用戶的ID
        user_id = get_jwt_identity()
        # 根據ID查詢用戶
        user = User.query.get(user_id)
        
        # 檢查用戶是否存在且是否為管理員角色
        if not user or user.role != UserRole.ADMIN:
            # 若不是管理員，返回禁止訪問錯誤信息
            return jsonify({'message': '需要管理員權限'}), 403
        
        # 若是管理員，則執行原始函數
        return fn(*args, **kwargs)
    
    # 保留原函數名稱，防止Flask路由註冊混亂
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/users', methods=['GET'])
@admin_required  # 使用自定義的管理員權限驗證裝飾器
def get_users():
    """管理員獲取所有使用者"""
    # 獲取分頁參數，默認為第1頁，每頁10條記錄
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 獲取搜尋和篩選參數
    search = request.args.get('search')  # 搜尋關鍵詞
    role = request.args.get('role')  # 角色篩選
    is_active = request.args.get('is_active')  # 狀態篩選
    
    # 創建基本查詢
    query = User.query
    
    # 根據搜尋關鍵詞進行篩選
    if search:
        # 使用OR條件搜尋使用者名稱或電子郵件中包含關鍵詞的記錄
        query = query.filter(
            (User.username.like(f'%{search}%')) |
            (User.email.like(f'%{search}%'))
        )
    
    # 根據角色進行篩選
    if role:
        # 將字串轉換為枚舉並應用篩選條件
        query = query.filter(User.role == UserRole(role))
    
    # 根據活躍狀態進行篩選
    if is_active is not None:
        # 將字串轉換為布林值
        is_active = is_active.lower() == 'true'
        # 應用篩選條件
        query = query.filter_by(is_active=is_active)
    
    # 應用分頁
    users_pagination = query.paginate(page=page, per_page=per_page)
    
    # 初始化空列表，用於存放格式化後的用戶數據
    users = []
    # 遍歷分頁後的用戶記錄
    for user in users_pagination.items:
        # 將用戶數據格式化為字典並添加到列表中
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,  # 將枚舉轉換為字串
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),  # 轉換為ISO格式字串
            'updated_at': user.updated_at.isoformat(),  # 轉換為ISO格式字串
            'url_count': len(user.urls)  # 計算該用戶創建的短網址數量
        })
    
    # 返回用戶列表和分頁信息
    return jsonify({
        'users': users,  # 用戶數據列表
        'total': users_pagination.total,  # 總記錄數
        'pages': users_pagination.pages,  # 總頁數
        'page': page,  # 當前頁碼
        'per_page': per_page  # 每頁記錄數
    }), 200  # HTTP 200狀態碼表示請求成功

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required  # 使用自定義的管理員權限驗證裝飾器
def get_user(user_id):
    """管理員獲取指定使用者詳情"""
    # 根據ID查詢用戶
    user = User.query.get(user_id)
    
    # 檢查用戶是否存在
    if not user:
        # 若不存在，返回不存在錯誤信息
        return jsonify({'message': '使用者不存在'}), 404
    
    # 初始化空列表，用於存放該用戶的短網址數據
    urls = []
    # 遍歷該用戶創建的所有短網址
    for url in user.urls:
        # 將短網址數據格式化為字典並添加到列表中
        urls.append({
            'id': url.id,
            'original_url': url.original_url,
            'short_code': url.short_code,
            'title': url.title,
            'created_at': url.created_at.isoformat(),  # 轉換為ISO格式字串
            'is_active': url.is_active,
            'visit_count': url.visit_count  # 訪問次數
        })
    
    # 返回用戶詳情和其創建的短網址列表
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,  # 將枚舉轉換為字串
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),  # 轉換為ISO格式字串
            'updated_at': user.updated_at.isoformat()  # 轉換為ISO格式字串
        },
        'urls': urls  # 短網址數據列表
    }), 200  # HTTP 200狀態碼表示請求成功

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required  # 使用自定義的管理員權限驗證裝飾器
def update_user(user_id):
    """管理員更新使用者資料"""
    # 根據ID查詢用戶
    user = User.query.get(user_id)
    
    # 檢查用戶是否存在
    if not user:
        # 若不存在，返回不存在錯誤信息
        return jsonify({'message': '使用者不存在'}), 404
    
    # 獲取通過JSON傳來的更新數據
    data = request.get_json()
    # 標記是否有數據更新
    updated = False
    
    # 更新電子郵件（如果提供了新的電子郵件且與當前不同）
    if 'email' in data and data['email'] != user.email:
        # 檢查新的電子郵件是否已被其他使用者使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            # 若電子郵件已被使用，返回衝突錯誤信息
            return jsonify({'message': '電子郵件已被使用'}), 409
        # 更新用戶的電子郵件
        user.email = data['email']
        updated = True
    
    # 更新角色（如果提供了新的角色）
    if 'role' in data:
        try:
            # 嘗試將字串轉換為角色枚舉
            new_role = UserRole(data['role'])
            # 更新用戶的角色
            user.role = new_role
            updated = True
        except ValueError:
            # 若角色值無效，返回錯誤信息
            return jsonify({'message': '無效的角色值'}), 400
    
    # 更新活躍狀態（如果提供了新的活躍狀態且與當前不同）
    if 'is_active' in data and data['is_active'] != user.is_active:
        # 更新用戶的活躍狀態
        user.is_active = data['is_active']
        updated = True
    
    # 重設密碼（如果請求中指定了重設密碼）
    if 'reset_password' in data and data['reset_password']:
        # 使用提供的新密碼或使用默認密碼 'password123'
        new_password = data.get('new_password', 'password123')
        # 將密碼進行雜湊處理
        user.password_hash = hash_password(new_password)
        updated = True
    
    # 如果有數據更新，則保存到資料庫
    if updated:
        # 提交事務，將更新持久化到資料庫
        db.session.commit()
        # 返回更新成功信息和更新後的用戶數據
        return jsonify({
            'message': '使用者資料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,  # 將枚舉轉換為字串
                'is_active': user.is_active
            }
        }), 200  # HTTP 200狀態碼表示請求成功
    else:
        # 若沒有數據更新，也返回成功信息
        return jsonify({'message': '無資料更新'}), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required  # 使用自定義的管理員權限驗證裝飾器
def delete_user(user_id):
    """管理員刪除使用者"""
    # 獲取當前已驗證管理員的ID
    current_user_id = get_jwt_identity()
    # 禁止管理員刪除自己的帳號
    if user_id == current_user_id:
        # 若嘗試刪除自己，返回禁止訪問錯誤信息
        return jsonify({'message': '無法刪除當前使用者'}), 403
    
    # 根據ID查詢用戶
    user = User.query.get(user_id)
    
    # 檢查用戶是否存在
    if not user:
        # 若不存在，返回不存在錯誤信息
        return jsonify({'message': '使用者不存在'}), 404
    
    # 從資料庫中刪除用戶
    db.session.delete(user)
    # 提交事務，將刪除操作持久化到資料庫
    db.session.commit()
    
    # 返回刪除成功信息
    return jsonify({'message': '使用者刪除成功'}), 200

@admin_bp.route('/stats', methods=['GET'])
@admin_required  # 使用自定義的管理員權限驗證裝飾器
def get_stats():
    """獲取站點統計資料"""
    # 計算使用者數量統計
    total_users = User.query.count()  # 總使用者數量
    active_users = User.query.filter_by(is_active=True).count()  # 活躍使用者數量
    
    # 計算短網址數量統計
    total_urls = URL.query.count()  # 總短網址數量
    active_urls = URL.query.filter_by(is_active=True).count()  # 活躍短網址數量
    
    # 計算總訪問數量
    total_visits = URLVisit.query.count()
    
    # 計算最近7天的每日訪問量
    now = datetime.utcnow()  # 獲取當前UTC時間
    week_ago = now - timedelta(days=7)  # 計算7天前的時間
    # 使用SQLAlchemy進行分組統計查詢
    daily_visits = db.session.query(
        func.date(URLVisit.timestamp).label('date'),  # 按日期分組
        func.count().label('count')  # 計算每日訪問次數
    ).filter(URLVisit.timestamp >= week_ago).group_by(  # 只統計最近7天
        func.date(URLVisit.timestamp)
    ).all()
    
    # 將查詢結果轉換為列表格式
    daily_stats = [
        {'date': str(date), 'count': count}
        for date, count in daily_visits
    ]
    
    # 查詢訪問量最高的前5個短網址
    top_urls = db.session.query(
        URL.id, URL.short_code, URL.original_url, URL.title,
        func.count(URLVisit.id).label('visit_count')  # 計算每個短網址的訪問次數
    ).join(URLVisit).group_by(URL.id).order_by(  # 使用JOIN關聯URL和訪問記錄表
        desc('visit_count')  # 按訪問次數降序排序
    ).limit(5).all()  # 只取前5個結果
    
    # 將查詢結果轉換為列表格式
    top_urls_list = [
        {
            'id': url_id,
            'short_code': short_code,
            'original_url': original_url,
            'title': title,
            'visit_count': visit_count
        }
        for url_id, short_code, original_url, title, visit_count in top_urls
    ]
    
    # 返回所有統計數據
    return jsonify({
        'users': {
            'total': total_users,
            'active': active_users
        },
        'urls': {
            'total': total_urls,
            'active': active_urls
        },
        'visits': {
            'total': total_visits,
            'daily': daily_stats
        },
        'top_urls': top_urls_list
    }), 200  # HTTP 200狀態碼表示請求成功
