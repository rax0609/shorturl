import os
from app import create_app
from flask import jsonify, redirect

# 建立 Flask 應用程式
app = create_app(os.getenv('FLASK_ENV', 'default'))

# 根路由
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': '短網址服務 API',
        'version': '1.0.0'
    })

# 短網址重定向路由
@app.route('/s/<short_code>', methods=['GET'])
def redirect_short_url(short_code):
    from app.models.models import URL, URLVisit, db
    from app.utils.helpers import get_client_info
    from datetime import datetime
    
    # 查詢短網址
    url = URL.query.filter_by(short_code=short_code).first()
    
    # 檢查是否存在
    if not url:
        return jsonify({'message': '短網址不存在'}), 404
    
    # 檢查是否啟用
    if not url.is_active:
        return jsonify({'message': '此短網址已被停用'}), 403
    
    # 檢查是否過期
    if url.expires_at and url.expires_at < datetime.utcnow():
        return jsonify({'message': '此短網址已過期'}), 403
    
    # 記錄訪問
    client_info = get_client_info()
    
    url_visit = URLVisit(
        url_id=url.id,
        ip_address=client_info['ip_address'],
        user_agent=client_info['user_agent'],
        referer=client_info['referer']
    )
    
    db.session.add(url_visit)
    db.session.commit()
    
    # 跳轉到原始網址
    return redirect(url.original_url)

def main():
    # 運行應用程式
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
