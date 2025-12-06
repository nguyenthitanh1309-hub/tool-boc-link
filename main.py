import os
import json
import hmac
import hashlib
import requests
import uuid
import time
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CẤU HÌNH API MOMO (PRODUCTION) ---
# Link chạy thật (Tiền thật)
MOMO_ENDPOINT = "https://payment.momo.vn/v2/gateway/api/create"

@app.route('/')
def home():
    return "<h1>Server MoMo Business đang chạy ngon lành! 🚀</h1>"

# --- API TẠO LINK THANH TOÁN DOANH NGHIỆP ---
@app.route('/api/create-momo', methods=['POST'])
def create_momo_link():
    try:
        data = request.get_json()
        
        # 1. Nhận thông tin từ Client (bà chị gửi lên)
        partnerCode = data.get('partnerCode')
        accessKey = data.get('accessKey')
        secretKey = data.get('secretKey')
        amount = str(data.get('amount')) # Số tiền (VD: "50000")
        orderInfo = data.get('orderInfo', "Thanh toan don hang")
        
        if not partnerCode or not accessKey or not secretKey:
            return jsonify({"status": "error", "message": "Thiếu Key rồi chị ơi!"}), 400

        # 2. Tạo các tham số bắt buộc (Theo chuẩn MoMo)
        requestId = str(uuid.uuid4())
        orderId = str(uuid.uuid4()) # Mã đơn hàng tự sinh (không trùng)
        redirectUrl = "https://google.com" # Thanh toán xong quay về đâu (Tùy chọn)
        ipnUrl = "https://google.com"      # Server nhận thông báo (Tùy chọn)
        requestType = "captureWallet"
        extraData = "" # Lưu email, sđt khách nếu cần
        
        # 3. Tạo Chữ Ký (Signature) - QUAN TRỌNG NHẤT
        # MoMo bắt buộc sắp xếp a-z: accessKey -> amount -> extraData ...
        rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
        
        # Mã hóa HMAC SHA256
        h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
        signature = h.hexdigest()

        # 4. Gửi lệnh sang MoMo
        payload = {
            'partnerCode': partnerCode,
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

        # Gọi API MoMo
        response = requests.post(MOMO_ENDPOINT, json=payload)
        result = response.json()

        # 5. Xử lý kết quả
        if result['resultCode'] == 0:
            # Thành công -> Trả về link thanh toán (payUrl)
            return jsonify({
                "status": "success",
                "payUrl": result['payUrl'], 
                "message": "Tạo link VIP thành công!"
            })
        else:
            # Thất bại (Do sai key, sai tiền...)
            return jsonify({
                "status": "error",
                "message": result.get('message', 'Lỗi không xác định'),
                "details": result
            })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
