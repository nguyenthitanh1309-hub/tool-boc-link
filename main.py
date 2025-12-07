import os
import uuid
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lấy key từ biến môi trường Render
PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
SECRET_KEY = os.getenv("MOMO_SECRET_KEY")

# Endpoint MoMo (sandbox hoặc production)
MOMO_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"  # đổi sang production nếu cần

@app.route("/create-payment", methods=["POST"])
def create_payment():
    try:
        # Nhận dữ liệu từ client
        req_data = request.get_json()
        amount = str(req_data.get("amount", "100000"))
        order_info = req_data.get("orderInfo", "Thanh toán đơn hàng")
        return_url = req_data.get("returnUrl", "https://yourdomain.com/return")
        notify_url = req_data.get("notifyUrl", "https://yourdomain.com/notify")

        # Tạo ID đơn hàng và request
        order_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        extra_data = ""

        # Tạo rawData để ký
        raw_data = f"accessKey={ACCESS_KEY}&amount={amount}&extraData={extra_data}&orderId={order_id}&orderInfo={order_info}&partnerCode={PARTNER_CODE}&redirectUrl={return_url}&requestId={request_id}&requestType=captureWallet&notifyUrl={notify_url}"

        # Tạo chữ ký SHA256
        signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            raw_data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # Tạo payload gửi MoMo
        payload = {
            "partnerCode": PARTNER_CODE,
            "accessKey": ACCESS_KEY,
            "requestId": request_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": return_url,
            "ipnUrl": notify_url,
            "extraData": extra_data,
            "requestType": "captureWallet",
            "signature": signature,
            "lang": "vi"
        }

        # Gửi request đến MoMo
        response = requests.post(MOMO_ENDPOINT, json=payload)
        result = response.json()

        # Trả về link thanh toán
        return jsonify({
            "payUrl": result.get("payUrl"),
            "orderId": order_id,
            "requestId": request_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
