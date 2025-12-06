import os
import json
import hmac
import hashlib
import requests
import uuid
import time
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)


PARTNER_CODE = "MOMOR3PG20251105_TEST"      
ACCESS_KEY = "GikWfAw9NBW1u5R"            
SECRET_KEY = "8XSbh21pbkVmxgBQL5Q7SsEEZc37vRy0"            
MOMO_ENDPOINT = "https://payment.momo.vn/v2/gateway/api/create"

# --- GIAO DIỆN TẠO LINK (Cho bà chị dùng) ---
@app.route('/admin-momo', methods=['GET', 'POST'])
def momo_generator():
    link_ket_qua = ""
    error_msg = ""
    
    if request.method == 'POST':
        try:
            # 1. Lấy số tiền và nội dung bả nhập từ Web
            amount_input = request.form.get('amount')
            note_input = request.form.get('note')
            
            # Xử lý số tiền (bỏ dấu chấm phẩy nếu có)
            amount = str(amount_input).replace(',', '').replace('.', '')
            
            # 2. Tạo bộ dữ liệu gửi sang MoMo
            requestId = str(uuid.uuid4())
            orderId = str(uuid.uuid4())
            redirectUrl = "https://google.com"
            ipnUrl = "https://google.com"
            requestType = "captureWallet"
            extraData = ""
            orderInfo = note_input if note_input else "Thanh toan don hang"
            
            # 3. Tạo Chữ Ký (Signature)
            rawSignature = f"accessKey={ACCESS_KEY}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={PARTNER_CODE}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
            
            h = hmac.new(bytes(SECRET_KEY, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
            signature = h.hexdigest()
            
            # 4. Gửi lệnh
            payload = {
                'partnerCode': PARTNER_CODE,
                'partnerName': "Store Payment",
                'storeId': "MomoStore",
                'requestId': requestId,
                'amount': amount,
                'orderId': orderId,
                'orderInfo': orderInfo,
                'redirectUrl': redirectUrl,
                'ipnUrl': ipnUrl,
                'lang': 'vi',
                'extraData': extraData,
                'requestType': requestType,
                'signature': signature
            }
            
            response = requests.post(MOMO_ENDPOINT, json=payload)
            result = response.json()
            
            if result['resultCode'] == 0:
                link_ket_qua = result['payUrl']
            else:
                error_msg = result.get('message', 'Lỗi không xác định')
                
        except Exception as e:
            error_msg = str(e)

    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Công cụ tạo Link MoMo VIP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; background: #f4f6f8; display: flex; justify-content: center; padding-top: 50px; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }}
            h2 {{ color: #d82d8b; text-align: center; margin-bottom: 20px; }} /* Màu hồng MoMo */
            input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #d82d8b; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #c21f7a; }}
            .result {{ margin-top: 20px; padding: 15px; background: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 6px; word-break: break-all; }}
            .error {{ margin-top: 20px; padding: 15px; background: #ffebee; border: 1px solid #ffcdd2; color: #c62828; border-radius: 6px; }}
            label {{ font-weight: bold; font-size: 14px; color: #555; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>💸 MoMo Link Generator</h2>
            <form method="POST">
                <label>Số tiền muốn thu (VNĐ):</label>
                <input type="number" name="amount" placeholder="Ví dụ: 20000" required>
                
                <label>Nội dung thu:</label>
                <input type="text" name="note" placeholder="Ví dụ: Mua the Garena 20k">
                
                <button type="submit">TẠO LINK NGAY</button>
            </form>
            
            {f'<div class="result"><b> Link của chị đây:</b><br><a href="{link_ket_qua}" target="_blank">Bấm vào đây để test</a><br><br><input type="text" value="{link_ket_qua}" readonly onclick="this.select()"></div>' if link_ket_qua else ''}
            
            {f'<div class="error"> Lỗi: {error_msg}</div>' if error_msg else ''}
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
