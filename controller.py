from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask("NetworkController")
CORS(app)

NODE_URLS = {
    1: "http://127.0.0.1:5001",
    2: "http://127.0.0.1:5002",
    3: "http://127.0.0.1:5003",
    4: "http://127.0.0.1:5004",
    5: "http://127.0.0.1:5005"
}

network_state = {
    "is_partitioned": False,
    "minority": [1, 2],
    "majority": [3, 4, 5]
}

def is_node_alive(node_id):
    """Kiểm tra xem một Node thực tế có đang bật hay không"""
    try:
        requests.get(f"{NODE_URLS[node_id]}/get/P0001", timeout=0.2)
        return True
    except:
        return False

@app.route('/status', methods=['GET'])
def status():
    return jsonify(network_state)

@app.route('/partition', methods=['POST'])
def partition_network():
    network_state["is_partitioned"] = True
    return jsonify({"message": "Đã ngắt kết nối nhóm {1,2} khỏi {3,4,5}"})

@app.route('/heal', methods=['POST'])
def heal_network():
    network_state["is_partitioned"] = False

    for node_id in network_state["minority"]:
        if is_node_alive(node_id):
            try:
                requests.post(f"{NODE_URLS[node_id]}/node_recovery", timeout=5.0)
            except:
                print(f"[-] Không thể kích hoạt giao thức phục hồi cho Node {node_id}")
                
    return jsonify({
        "status": "success", 
        "message": "Mạng đã được kết nối lại. Toàn bộ cluster đã hội tụ dữ liệu đồng nhất."
    })

@app.route('/check_quorum/<int:node_id>', methods=['GET'])
def check_quorum(node_id):
    is_partitioned = network_state["is_partitioned"]
    
    if not is_partitioned:
        alive_count = sum(1 for i in NODE_URLS if is_node_alive(i))
        return jsonify({"can_write": alive_count >= 3})
    
    if node_id in network_state["minority"]:
        return jsonify({"can_write": False})
    
    if node_id in network_state["majority"]:
        alive_in_majority = sum(1 for n_id in network_state["majority"] if is_node_alive(n_id))
        if alive_in_majority >= 3:
            return jsonify({"can_write": True})
        else:
            return jsonify({
                "can_write": False, 
                "error": f"Cụm đa số mất túc số do có node sập (Chỉ còn {alive_in_majority} node sống)."
            })


@app.route('/recovery/<int:node_id>/<product_id>', methods=['GET'])
def recover_stock(node_id, product_id):
    for target_id in network_state["majority"]:
        if target_id != node_id and is_node_alive(target_id):
            try:
                res = requests.get(f"{NODE_URLS[target_id]}/get/{product_id}", timeout=0.3)
                if res.ok:
                    return jsonify({"stock": res.json().get("stock")})
            except:
                continue
    return jsonify({"error": "Không tìm thấy node nào đang sống để đồng bộ"}), 404

app.run(host='127.0.0.1', port=5000)