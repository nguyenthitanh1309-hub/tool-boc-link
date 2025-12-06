import os
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)


RECEIVER_PHONE = "01663606953" 
# Tên người nhận 
RECEIVER_NAME = "TRAN HAI YEN"

@app.route('/admin-momo', methods=['GET', 'POST'])
def generator():
    gen_link = ""
    if request.method == 'POST':
        amount = request.form.get('amount')
        note = request.form.get('note')
        
        # Tạo Deep Link (Mở App)
        # Cấu trúc: momo://?action=transfer&receiver=SDT&amount=TIEN&note=NOIDUNG
        deep_link = f"momo://?action=transfer&receiver={RECEIVER_PHONE}&amount={amount}&note={note}"
        
        # Mã hóa để giấu link
        encoded = base64.b64encode(deep_link.encode('utf-8')).decode('utf-8')
        host_url = request.host_url.rstrip('/')
        gen_link = f"{host_url}/?data={encoded}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tool Tạo Link Mở App</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; padding: 20px; text-align: center; }}
            input, button {{ width: 100%; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; }}
            button {{ background: #a50064; color: white; font-weight: bold; border: none; }}
            .result {{ background: #eee; padding: 15px; word-break: break-all; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <h2 Tạo Link Mở App MoMo</h2>
        <form method="POST">
            <input type="number" name="amount" placeholder="Nhập số tiền" required>
            <input type="text" name="note" placeholder="Nội dung thu tiền">
            <button type="submit">TẠO LINK</button>
        </form>
        {f'<div class="result"><b>Link của chị đây:</b><br><a href="{gen_link}">{gen_link}</a></div>' if gen_link else ''}
    </body>
    </html>
    """

@app.route('/')
def redirect_to_app():
    data = request.args.get('data')
    if not data: return "Lỗi: Link hỏng rồi"
    
    # Giải mã ra cái link momo://
    try:
        momo_schema = base64.b64decode(data).decode('utf-8')
    except:
        return "Lỗi giải mã"

    # Link dự phòng (Nếu khách không cài App thì mở web)
    # Dùng link me.momo.vn để không bị lỗi
    fallback_url = f"https://me.momo.vn/{RECEIVER_PHONE}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Đang mở MoMo...</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background-color: #a50064; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; color: white; font-family: sans-serif; text-align: center; }}
            .loader {{ border: 4px solid #f3f3f3; border-top: 4px solid #ff4081; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 20px; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .btn {{ margin-top: 20px; padding: 10px 20px; background: white; color: #a50064; text-decoration: none; border-radius: 20px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <h3>Đang mở App MoMo...</h3>
        <p>Vui lòng đợi trong giây lát</p>
        
        <a id="btnOpen" href="{momo_schema}" class="btn">Bấm vào đây nếu không tự mở</a>

        <script>
            // Tự động kích hoạt mở App ngay khi vào web
            setTimeout(function() {{
                window.location.href = "{momo_schema}";
            }}, 500);

            // Nếu sau 3 giây không mở được (do chưa cài app), thì chuyển sang web
            setTimeout(function() {{
                // window.location.href = "{fallback_url}"; 
            }}, 3000);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
