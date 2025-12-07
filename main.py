import os
import uuid
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lấy key từ biến môi trường
PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
SECRET_KEY = os.getenv("MOMO_SECRET_KEY")

# Endpoint MoMo (sandbox)
MOMO_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"

@app.route("/", methods=["GET"])
def home():
    return "MoMo API đang chạy!"

@app.route("/create-payment", methods=["POST"])
def create_payment():
    try:
        # Hỗ trợ cả JSON và form
        if request.is_json:
            req_data = request.get_json()
        else:
            req_data = request.form

        amount = str(req_data.get("amount", "100000"))
        order_info = req_data.get("orderInfo", "Thanh toán đơn hàng")
        return_url = req_data.get("returnUrl", "https://yourdomain.com/return")
        notify_url = req_data.get("notifyUrl", "https://yourdomain.com/notify")

        order_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        extra_data = ""

        raw_data = f"accessKey={ACCESS_KEY}&amount={amount}&extraData={extra_data}&orderId={order_id}&orderInfo={order_info}&partnerCode={PARTNER_CODE}&redirectUrl={return_url}&requestId={request_id}&requestType=captureWallet&notifyUrl={notify_url}"

        signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            raw_data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

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

        response = requests.post(MOMO_ENDPOINT, json=payload)
        result = response.json()

        return jsonify({
            "payUrl": result.get("payUrl"),
            "orderId": order_id,
            "requestId": request_id,
            "momoResponse": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
