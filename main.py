import os
import uuid
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Lấy key từ biến môi trường
PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
SECRET_KEY = os.getenv("MOMO_SECRET_KEY")
MOMO_ENDPOINT = "https://payment.momo.vn/v2/gateway/api/create"

@app.route("/", methods=["GET"])
def home():
    return "MoMo Production API đang hoạt động!"

@app.route("/create", methods=["GET", "POST"])
def create_page():
    link_ket_qua = ""
    error_msg = ""

    if request.method == "POST":
        try:
            amount_input = request.form.get("amount")
            note_input = request.form.get("note")

            amount = str(amount_input).replace(",", "").replace(".", "")
            order_info = note_input if note_input else "Thanh toán đơn hàng"
            order_id = str(uuid.uuid4())
            request_id = str(uuid.uuid4())
            redirect_url = "https://google.com"
            ipn_url = "https://google.com"
            extra_data = ""
            request_type = "captureWallet"

            raw_signature = (
                f"accessKey={ACCESS_KEY}"
                f"&amount={amount}"
                f"&extraData={extra_data}"
                f"&ipnUrl={ipn_url}"
                f"&orderId={order_id}"
                f"&orderInfo={order_info}"
                f"&partnerCode={PARTNER_CODE}"
                f"&redirectUrl={redirect_url}"
                f"&requestId={request_id}"
                f"&requestType={request_type}"
            )

            signature = hmac.new(
                SECRET_KEY.encode("utf-8"),
                raw_signature.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            payload = {
                "partnerCode": PARTNER_CODE,
                "accessKey": ACCESS_KEY,
                "requestId": request_id,
                "amount": amount,
                "orderId": order_id,
                "orderInfo": order_info,
                "redirectUrl": redirect_url,
                "ipnUrl": ipn_url,
                "extraData": extra_data,
                "requestType": request_type,
                "signature": signature,
                "lang": "vi"
            }

            response = requests.post(MOMO_ENDPOINT, json=payload)
            result = response.json()

            if result.get("resultCode") == 0:
                link_ket_qua = result.get("payUrl")
            else:
                error_msg = result.get("message", "Lỗi không xác định")

        except Exception as e:
            error_msg = str(e)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MoMo Link Generator</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: sans-serif; background: #f4f6f8; display: flex; justify-content: center; padding-top: 50px; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }}
            h2 {{ color: #d82d8b; text-align: center; margin-bottom: 20px; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #d82d8b; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #c21f7a; }}
            .result {{ margin-top: 20px; padding: 15px; background: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 6px; word-break: break-word; }}
            .error {{ margin-top: 20px; padding: 15px; background: #ffebee; border: 1px solid #ffcdd2; color: #c62828; border-radius: 6px; }}
            label {{ font-weight: bold; font-size: 14px; color: #555; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>MoMo Link Generator</h2>
            <form method="POST">
                <label>Số tiền muốn thu (VNĐ):</label>
                <input type="number" name="amount" placeholder="Ví dụ: 20000" required>
                <label>Nội dung thu:</label>
                <input type="text" name="note" placeholder="Ví dụ: Mua thẻ Garena 20k">
                <button type="submit">TẠO LINK NGAY</button>
            </form>
            {% if link_ket_qua %}
                <div class="result">
                    <b>Link thanh toán:</b><br>
                    <a href="{{ link_ket_qua }}" target="_blank">Bấm vào đây để mở</a><br><br>
                    <input type="text" value="{{ link_ket_qua }}" readonly onclick="this.select()">
                </div>
            {% endif %}
            {% if error_msg %}
                <div class="error">Lỗi: {{ error_msg }}</div>
            {% endif %}
        </div>
    </body>
    </html>
    """, link_ket_qua=link_ket_qua, error_msg=error_msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
