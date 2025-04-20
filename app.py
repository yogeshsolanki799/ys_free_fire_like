from flask import Flask, request, jsonify
import json
import random
import requests
import like_pb2, like_count_pb2, uid_generator_pb2
from Crypto.Cipher import AES
import base64
import os

app = Flask(__name__)

# AES Encryption Key
key = b"y9A7xk3LsW8vBt1H"
iv = b"2b7e151628aed2a6"

# Load region tokens
def load_tokens(region):
    file_path = f"token_{region.lower()}.json"
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return [d["token"] for d in data]
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return []

# Encrypt request using AES
def encrypt_request(data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
    encrypted = cipher.encrypt(padded.encode())
    return base64.b64encode(encrypted).decode()

# Like sender function
def send_like(uid, token):
    url = "https://cs.freefiremobile.com/api/player/get_user_info_v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "FreeFire/1.92.0 (Android; 10)"
    }

    req = like_pb2.LikeRequest()
    req.target_uid = int(uid)
    req.count = 1
    encrypted_data = encrypt_request(req.SerializeToString().hex())

    response = requests.post(url, data={"data": encrypted_data}, headers=headers)
    return response.status_code == 200

# Flask route
@app.route('/like', methods=['GET'])
def like():
    uid = request.args.get("uid")
    region = request.args.get("server_name", "IND").upper()

    if not uid or not uid.isdigit():
        return jsonify({"status": "error", "message": "Invalid UID"}), 400

    tokens = load_tokens(region)
    if not tokens:
        return jsonify({"status": "error", "message": "No tokens available"}), 500

    token = random.choice(tokens)
    success = send_like(uid, token)

    if success:
        return jsonify({"status": "success", "message": f"Like sent to {uid}"})
    else:
        return jsonify({"status": "error", "message": "Failed to send like"}), 500

if __name__ == '__main__':
    app.run(debug=True)