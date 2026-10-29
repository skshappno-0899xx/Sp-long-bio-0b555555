###Hey baby 🍼 If you leak this file under your own name and claim the credit, I'll fuck you with salt. 🥱

from flask import Flask, request, jsonify, make_response
import requests
import binascii
import urllib3
import base64
import json
import random
import sys
import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ============================================================
#  Constants
# ============================================================

FREEFIRE_UPDATE_URL = "https://clientbp.ppmainecoonghj.com/UpdateSocialBasicInfo"
TOKEN_API_URL = "https://http://jwtt-eta.vercel.app/token"

FREEFIRE_VERSION = os.environ.get("FREEFIRE_VERSION", "OB55")

# Bio encryption keys
KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])


# ============================================================
#  Device Database
# ============================================================

DEVICES = [
    {"model": "SM-G998B", "android": "13", "api": "33", "cpu": "ARMv8 | 2800 | 8", "gpu": "Mali-G78", "res": ["1440", "1080"], "dpi": "480", "ram": "8192", "build": "TP1A.220624.014"},
    {"model": "realme C31", "android": "12", "api": "31", "cpu": "ARMv8 | 2000 | 8", "gpu": "Mali-G52", "res": ["720", "1600"], "dpi": "320", "ram": "4096", "build": "SQ3A.220705.003"},
    {"model": "Mi 11", "android": "12", "api": "32", "cpu": "ARMv8 | 2500 | 8", "gpu": "Adreno 650", "res": ["1080", "2400"], "dpi": "395", "ram": "6144", "build": "SQ3A.220705.003"},
    {"model": "OnePlus 9", "android": "13", "api": "33", "cpu": "ARMv8 | 2900 | 8", "gpu": "Adreno 660", "res": ["1080", "2400"], "dpi": "420", "ram": "8192", "build": "TP1A.220624.014"},
    {"model": "Pixel 6", "android": "13", "api": "33", "cpu": "ARMv8 | 2800 | 8", "gpu": "Mali-G78", "res": ["1080", "2400"], "dpi": "440", "ram": "8192", "build": "TP1A.220624.014"},
]

def get_random_device():
    device = random.choice(DEVICES)
    return {
        "model": device["model"],
        "android": device["android"],
        "api": device["api"],
        "cpu": device["cpu"],
        "gpu": device["gpu"],
        "width": device["res"][0],
        "height": device["res"][1],
        "dpi": device["dpi"],
        "ram": device["ram"],
        "build": device["build"]
    }

def encrypt_data(data_bytes):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)


# ============================================================
#  Bio Protobuf Setup
# ============================================================

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto\"\xbb\x01\n\x04\x44\x61ta\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x1e\n\x07\x66ield_5\x18\x05 \x01(\x0b\x32\r.EmptyMessage\x12\x1e\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\r.EmptyMessage\x12\x0f\n\x07\x66ield_8\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield_9\x18\t \x01(\x05\x12\x1f\n\x08\x66ield_11\x18\x0b \x01(\x0b\x32\r.EmptyMessage\x12\x1f\n\x08\x66ield_12\x18\x0c \x01(\x0b\x32\r.EmptyMessage\"\x0e\n\x0c\x45mptyMessageb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', _globals)
BioData = _sym_db.GetSymbol('Data')
EmptyMessage = _sym_db.GetSymbol('EmptyMessage')


# ============================================================
#  JWT via External Shappno API
# ============================================================

def get_jwt_from_shappno_api(uid, password):
    """Fetch JWT from Shappno Token API using uid + password"""
    try:
        print(f"[🔍] Fetching JWT from Shappno API for UID: {uid}")
        url = f"{TOKEN_API_URL}?uid={uid}&password={password}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        res = requests.get(url, headers=headers, verify=False, timeout=30)
        data = res.json()

        if data.get("status") == "success" and data.get("token"):
            print(f"[✅] JWT received from Shappno API")
            return {
                "token": data.get("token"),
                "access_token": data.get("access_token"),
                "open_id": data.get("open_id"),
                "real_uid": data.get("real_uid"),
                "time": data.get("time")
            }
        else:
            print(f"[❌] Shappno API error: {data}")
            return None
    except Exception as e:
        print(f"[❌] Shappno API exception: {str(e)}")
        return None


# ============================================================
#  JWT Info Decode
# ============================================================

SECRET_KEY = b"1e5898ccb8dfdd921f9bdea848768b64a201"

def decode_nickname(encoded: str) -> str:
    try:
        raw = base64.b64decode(encoded)
        dec = bytearray()
        for i, b in enumerate(raw):
            dec.append(b ^ SECRET_KEY[i % len(SECRET_KEY)])
        return dec.decode('utf-8', errors='replace')
    except Exception:
        return encoded


def decode_jwt_info(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, None, None
        payload_b64 = parts[1]
        payload_b64 += '=' * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
        uid = payload.get("account_id")
        region = payload.get("lock_region")
        nickname = payload.get("nickname")
        if isinstance(nickname, str):
            nickname = decode_nickname(nickname)
        return str(uid), nickname, region
    except Exception:
        return None, None, None


# ============================================================
#  Bio Upload
# ============================================================

def upload_bio_request(jwt_token, bio_text):
    try:
        data = BioData()
        data.field_2 = 17
        data.field_5.CopyFrom(EmptyMessage())
        data.field_6.CopyFrom(EmptyMessage())
        data.field_8 = bio_text
        data.field_9 = 1
        data.field_11.CopyFrom(EmptyMessage())
        data.field_12.CopyFrom(EmptyMessage())

        data_bytes = data.SerializeToString()
        encrypted = encrypt_data(data_bytes)

        device = get_random_device()
        headers = {
            "Expect": "100-continue",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": FREEFIRE_VERSION,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android {device['android']}; {device['model']})",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Authorization": f"Bearer {jwt_token}"
        }

        resp = requests.post(FREEFIRE_UPDATE_URL, headers=headers,
                             data=encrypted, timeout=30, verify=False)

        if resp.status_code == 200:
            status_text = "✅ Success"
        elif resp.status_code == 401:
            status_text = "❌ Unauthorized (Invalid JWT)"
        else:
            status_text = f"⚠️ Status {resp.status_code}"

        return {
            "status": status_text,
            "code": resp.status_code,
            "bio": bio_text,
            "server_response": binascii.hexlify(resp.content).decode('utf-8')
        }
    except Exception as e:
        return {"status": f"Error: {str(e)}", "code": 500,
                "bio": bio_text, "server_response": "N/A"}


# ============================================================
#  Routes
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "api": "Long Bio API (OB55)",
        "credit": "SHAPPNO GMR",
        "telegram": "@SHAPPNO_CODEX",
        "version": FREEFIRE_VERSION,
        "status": "running ✅",
        "token_api": TOKEN_API_URL,
        "endpoints": {
            "/bio_upload": {
                "method": "GET/POST",
                "params": {
                    "bio": "string (required)",
                    "jwt": "string (optional - direct JWT)",
                    "uid": "string (optional - with pass)",
                    "pass": "string (optional - with uid)"
                }
            }
        }
    })


@app.route("/bio_upload", methods=["GET", "POST"])
def combined_bio_upload():
    bio = request.args.get("bio") or request.form.get("bio")
    jwt_token = request.args.get("jwt") or request.form.get("jwt")
    uid = request.args.get("uid") or request.form.get("uid")
    password = request.args.get("pass") or request.form.get("pass")

    if not bio:
        return jsonify({"status": "❌ Error", "code": 400,
                        "error": "Missing 'bio' parameter"}), 400

    final_jwt = None
    login_method = "Direct JWT"
    final_open_id = None
    final_access_token = None
    final_uid = None
    final_name = None
    final_region = None

    # Option 1: Direct JWT
    if jwt_token:
        final_jwt = jwt_token
        j_uid, j_name, j_region = decode_jwt_info(jwt_token)
        final_uid = j_uid
        final_name = j_name
        final_region = j_region

    # Option 2: UID + Password → Shappno Token API
    elif uid and password:
        login_method = "UID/Pass → Shappno Token API"
        result = get_jwt_from_shappno_api(uid, password)
        if result and result.get("token"):
            final_jwt = result["token"]
            final_access_token = result.get("access_token")
            final_open_id = result.get("open_id")
            j_uid, j_name, j_region = decode_jwt_info(final_jwt)
            final_uid = j_uid or result.get("real_uid")
            final_name = j_name
            final_region = j_region
        else:
            return jsonify({
                "status": "❌ Token API Failed",
                "code": 401,
                "error": "Shappno Token API থেকে JWT পাওয়া যায়নি"
            }), 401

    else:
        return jsonify({
            "status": "❌ Error",
            "code": 400,
            "error": "Provide JWT, or UID + Password"
        }), 400

    if not final_jwt:
        return jsonify({"status": "❌ JWT Missing", "code": 500}), 500

    result = upload_bio_request(final_jwt, bio)

    response_data = {
        "Credit": "SHAPPNO GMR",
        "Join For More": "Telegram: @SHAPPNO_CODEX",
        "status": result["status"],
        "login_method": login_method,
        "code": result["code"],
        "bio": result["bio"],
        "uid": str(final_uid) if final_uid else None,
        "name": final_name,
        "region": final_region,
        "open_id": final_open_id,
        "access_token": final_access_token,
        "server_response": result["server_response"],
        "generated_jwt": final_jwt,
        "version": FREEFIRE_VERSION
    }

    response = make_response(jsonify(response_data))
    response.headers["Content-Type"] = "application/json"
    return response


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=False)