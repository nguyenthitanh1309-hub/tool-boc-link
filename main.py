import os
import base64
from flask import Flask, request, render_template_string, jsonify

# --- KHỞI TẠO APP ---
app = Flask(__name__)

# --- CẤU HÌNH GIAO DIỆN MESSENGER ---
META_CONFIG = {
    "title": "Hóa đơn thanh toán điện tử",
    "desc": "Vui lòng hoàn tất đơn hàng. Giao dịch được bảo mật.",
    "image": "https://cdn-icons-png.flaticon.com/512/10103/10103287.png"
}

# --- 1. TRANG CHÍNH: Xử lý chuyển hướng (Khách hàng vào đây) ---
@app.route('/')
def home():
    encoded_url = request.args.get('id')
    # Nếu không có ID -> Báo lỗi 404
    if not encoded_url:
        return "<h1>404 - Page Not Found</h1>", 404
    
    try:
        # Giải mã link gốc
        target_url = base64.b64decode(encoded_url).decode('utf-8')
    except:
        return "<h1>Invalid Link</h1>", 400

    # Giao diện chờ "Fake" hóa đơn
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>{META_CONFIG['title']}</title>
        <meta property="og:title" content="{META_CONFIG['title']}" />
        <meta property="og:description" content="{META_CONFIG['desc']}" />
        <meta property="og:image" content="{META_CONFIG['image']}" />
        <meta property="og:type" content="website" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f2f5; text-align: center; }}
            .loader {{ border: 4px solid #f3f3f3; border-top: 4px solid #0084ff; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 20px; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
        <script>
            setTimeout(function() {{ window.location.href = "{target_url}"; }}, 1500);
        </script>
    </head>
    <body>
        <div class="loader"></div>
        <div>Đang xác thực giao dịch...</div>
    </body>
    </html>
    """
    return render_template_string(html_content)

# --- 2. CÁI CŨ: Trang tạo link thủ công (Cho người dùng) ---
@app.route('/create', methods=['GET', 'POST'])
def create_link_manual():
    generated_link = ""
    if request.method == 'POST':
        original_url = request.form.get('url')
        if original_url:
            encoded = base64.b64encode(original_url.encode('utf-8')).decode('utf-8')
            host_url = request.host_url.rstrip('/')
            generated_link = f"{host_url}/?id={encoded}"
            
    # Giao diện HTML đơn giản
    return f"""
    <div style="font-family: sans-serif; padding: 50px; text-align: center;">
        <h2>Tool Bọc Link Pro (Manual)</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Dán link gốc vào đây" style="width: 300px; padding: 10px;" required>
            <br><br>
            <button type="submit" style="padding: 10px 20px; background: #0084ff; color: white; border: none; cursor: pointer;">Tạo Link</button>
        </form>
        <br>
        {f'<div style="background: #e9ecef; padding: 15px; word-break: break-all;">Link của bạn:<br><a href="{generated_link}">{generated_link}</a></div>' if generated_link else ''}
    </div>
    """

# --- 3. CÁI MỚI: API tự động (Cho lập trình viên/Tool khác) ---
@app.route('/api/create', methods=['POST'])
def create_link_api():
    try:
        data = request.get_json()
        original_url = data.get('url')
        
        if not original_url:
            return jsonify({"status": "error", "message": "Thiếu tham số 'url'"}), 400
            
        encoded = base64.b64encode(original_url.encode('utf-8')).decode('utf-8')
        host_url = request.host_url.rstrip('/')
        final_link = f"{host_url}/?id={encoded}"
        
        return jsonify({
            "status": "success",
            "original_url": original_url,
            "cloaked_link": final_link
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- CHẠY APP ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
