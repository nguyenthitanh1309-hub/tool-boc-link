import os
import base64
import urllib.parse # <--- THÊM CÁI NÀY
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- CẤU HÌNH ---
RECEIVER_PHONE = "01663606953"  # <--- Nhớ thay số bà chị vào đây (viết liền)
RECEIVER_NAME = "Shop Ba Chi"

@app.route('/admin-momo', methods=['GET', 'POST'])
def generator():
    gen_link = ""
    if request.method == 'POST':
        amount = request.form.get('amount')
        note = request.form.get('note')
        
        # --- FIX LỖI Ở ĐÂY ---
        # Mã hóa nội dung (Ví dụ: "Mua thẻ" -> "Mua%20th%E1%BA%BB")
        note_safe = urllib.parse.quote(note)
        
        # Tạo link Mở App (Dùng format chuẩn nhất hiện nay)
        # Cách 1: Dùng momo:// (Mở trực tiếp)
        deep_link = f"momo://?action=transfer&receiver={RECEIVER_PHONE}&amount={amount}&note={note_safe}"
        
        # Cách 2 (Dự phòng): Dùng link me.momo.vn (Link định danh, ổn định hơn)
        # deep_link = f"https://me.momo.vn/{RECEIVER_PHONE}?amount={amount}&message={note_safe}"
        
        # Mã hóa Base64 để giấu link
        encoded = base64.b64encode(deep_link.encode('utf-8')).decode('utf-8')
        host_url = request.host_url.rstrip('/')
        gen_link = f"{host_url}/?data={encoded}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tool Tạo Link MoMo VIP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; padding: 20px; text-align: center; background: #f4f4f4; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            input, button {{ width: 100%; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }}
            button {{ background: #a50064; color: white; font-weight: bold; border: none; cursor: pointer; }}
            .result {{ background: #e1bee7; padding: 15px; word-break: break-all; border-radius: 8px; margin-top: 15px; color: #4a0072; }}
            a {{ color: #a50064; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>⚡ Tạo Link Mở App</h2>
            <form method="POST">
                <input type="number" name="amount" placeholder="Nhập số tiền" required>
                <input type="text" name="note" placeholder="mã đơn hàng">
                <button type="submit">TẠO LINK</button>
            </form>
            {f'<div class="result">Link mới:<br><br><a href="{gen_link}">{gen_link}</a></div>' if gen_link else ''}
        </div>
    </body>
    </html>
    """

@app.route('/')
def redirect_to_app():
    data = request.args.get('data')
    if not data: return "Lỗi: Link hỏng rồi!"
    
    try:
        momo_schema = base64.b64decode(data).decode('utf-8')
    except:
        return "Lỗi giải mã"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mở MoMo...</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script>
            // Tự động mở App
            window.location.href = "{momo_schema}";
            
            // Nếu sau 2 giây không mở được, hiện nút bấm
            setTimeout(function() {{
                document.getElementById('manual-btn').style.display = 'block';
            }}, 2000);
        </script>
        <style>
            body {{ background-color: #a50064; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }}
            .btn {{ display: none; padding: 12px 24px; background: white; color: #a50064; text-decoration: none; border-radius: 25px; font-weight: bold; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h3>Đang mở App MoMo...</h3>
        <p>Vui lòng đợi 1 chút</p>
        <a id="manual-btn" href="{momo_schema}" class="btn">BẤM VÀO ĐÂY ĐỂ MỞ</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
