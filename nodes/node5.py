from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import os

NODE_ID = 5
PORT = 5005
CONTROLLER_URL = 'http://127.0.0.1:5000'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, f'node{NODE_ID}.sqlite3')

LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs', f'node{NODE_ID}.log'))

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

app = Flask(__name__)
CORS(app)

def log_message(msg):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg)

@app.route('/get/<key>', methods=['GET'])
def get_val(key):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT stock FROM products WHERE product_id=?", (key,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return jsonify({"stock": row[0]})
    return jsonify({"error": "Not found"}), 404

@app.route('/set/<key>', methods=['POST'])
def set_val(key):
    check_res = requests.get(f"{CONTROLLER_URL}/check_quorum/{NODE_ID}")
    can_write = check_res.json().get("can_write", False)
    
    if not can_write:
        msg = f"Node {NODE_ID} bị chặn lệnh Ghi do thuộc cụm thiểu số (Read-Only)."
        log_message(f"[DENIED] {msg}")
        return jsonify({"error": msg}), 403

    data = request.json
    new_stock = data['stock']
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock=? WHERE product_id=?", (new_stock, key))
    conn.commit()
    conn.close()
    
    log_message(f"[WRITE] Cập nhật {key} -> {new_stock}")
    return jsonify({"status": "success", "stock": new_stock})


@app.route('/node_recovery', methods=['POST'])
def trigger_node_recovery():
    """Endpoint cho phép Controller ra lệnh cho Node tự sửa lỗi toàn bộ dữ liệu"""
    recover_data()
    return jsonify({
        "status": "success", 
        "message": f"Node {NODE_ID} đã thực hiện Catch-up toàn bộ sản phẩm thành công."
    })

def recover_data():
    print(f"[*] Node {NODE_ID} đang khởi động... Xin dữ liệu chuẩn từ Controller...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT product_id FROM products")
    products = cur.fetchall()
    
    recovered_count = 0
    for (p_id,) in products:
        try:
            res = requests.get(f"{CONTROLLER_URL}/recovery/{NODE_ID}/{p_id}", timeout=0.5)
            if res.status_code == 200:
                correct_stock = res.json().get("stock")
                cur.execute("UPDATE products SET stock=? WHERE product_id=?", (correct_stock, p_id))
                recovered_count += 1
        except:
            pass 
            
    conn.commit()
    conn.close()
    print(f"[+] Phục hồi hoàn tất. Đã đồng bộ {recovered_count} sản phẩm với mạng lưới.")

recover_data()

app.run(host='127.0.0.1', port=PORT)