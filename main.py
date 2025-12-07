import os
import uuid
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
SECRET_KEY = os.getenv("MOMO_SECRET_KEY")
MOMO_ENDPOINT = "https://payment.momo.vn/v2/gateway/api/create"

@app.route("/", methods=["GET"])
def home():
    return "MoMo Production API đang hoạt động!"

@app.route("/create-payment", methods=["POST"])
def create_payment():
    try:
        req_data = request.get_json(force=True)

        amount = str(req_data.get("amount", "100000"))
        order_info = req_data.get("orderInfo", "Thanh toán đơn hàng")
        return_url = req_data.get("returnUrl", "https://yourdomain.com/return")
        notify_url = req_data.get("notifyUrl", "https://yourdomain.com/notify")

        order_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        extra_data = ""
        request_type = "captureWallet"

        raw_signature = (
            f"accessKey={ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={notify_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={PARTNER_CODE}"
            f"&redirectUrl={return_url}"
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
            "redirectUrl": return_url,
            "ipnUrl": notify_url,
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature,
            "lang": "vi"
        }

        response = requests.post(MOMO_ENDPOINT, json=payload)
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
