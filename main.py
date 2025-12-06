import os
import base64
import urllib.parse
import uuid
import datetime
from flask import Flask, request, render_template_string

app = Flask(__name__)



RECEIVER_PHONE = "01663606953"  

RECEIVER_NAME = "TRAN HAI YEN" 

@app.route('/admin-momo', methods=['GET', 'POST'])
def generator():
    gen_link = ""
    if request.method == 'POST':
        amount = request.form.get('amount')
        note = request.form.get('note')
        
        # Tạo hóa đơn Fake
        fake_order_id = uuid.uuid4().hex[:16].upper() # Mã đơn hàng nhìn cho uy tín
        invoice_data = f"{amount}|{note}|{fake_order_id}"
        
        encoded = base64.b64encode(invoice_data.encode('utf-8')).decode('utf-8')
        host_url = request.host_url.rstrip('/')
        gen_link = f"{host_url}/?data={encoded}"

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; padding: 20px; text-align: center; }}
            input, button {{ width: 100%; padding: 15px; margin: 10px 0; }}
            button {{ background: #d82d8b; color: white; font-weight: bold; border: none; }}
        </style>
    </head>
    <body>
        <h2>tool bọc link</h2>
        <form method="POST">
            <input type="number" name="amount" placeholder="Số tiền" required>
            <input type="text" name="note" placeholder="Mã Hóa Đơn">
            <button type="submit">TẠO LINK</button>
        </form>
        {f'<div>Copy link:<br><a href="{gen_link}">{gen_link}</a></div>' if gen_link else ''}
    </body>
    </html>
    """

@app.route('/')
def show_invoice():
    data = request.args.get('data')
    if not data: return "Lỗi link!"
    
    try:
        decoded = base64.b64decode(data).decode('utf-8')
        amount, note, order_id = decoded.split('|')
        amount_formatted = "{:,.0f}".format(int(amount)).replace(",", ".") + "đ"
        
        # --- CHIÊU MỚI: DÙNG LINK me.momo.vn (Ổn định hơn momo://) ---
        # Link này tự động gọi App và điền tiền
        note_safe = urllib.parse.quote(note)
        # Cấu trúc: https://me.momo.vn/SDT?amount=TIEN&message=NOIDUNG
        deep_link = f"https://me.momo.vn/{RECEIVER_PHONE}?amount={amount}&message={note_safe}"
        
    except:
        return "Lỗi dữ liệu!"

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <title>Thanh toán MoMo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f4f6f8; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }}
            .btn {{ display: block; width: 100%; padding: 15px; background: #d82d8b; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h3>{RECEIVER_NAME}</h3>
            <h1 style="color:#d82d8b">{amount_formatted}</h1>
            <p>{note}</p>
            <p style="color:#888; font-size:12px">Mã đơn: {order_id}</p>
            
            <a href="{deep_link}" class="btn">MỞ APP THANH TOÁN NGAY</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

