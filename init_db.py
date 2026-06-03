import sqlite3
import csv
import os

def init_node_db(node_id: int, csv_path: str) -> None:
    """
    Khởi tạo database SQLite cho một node và nạp dữ liệu từ file CSV.
    
    Args:
        node_id: ID của node (từ 1 đến 5).
        csv_path: Đường dẫn tới file dataset.csv.
    """
    db_path = f"nodes/node{node_id}.sqlite3"

    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            stock INTEGER NOT NULL
        )
    ''')

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            cursor.execute('''
                INSERT INTO products (product_id, stock)
                VALUES (?, ?)
            ''', (row['product_id'], int(row['stock'])))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Node {node_id} khởi tạo thành công với {count} bản ghi. (File: {db_path})")

os.makedirs("nodes", exist_ok=True)
csv_file = "dataset.csv"
num_nodes = 5

print(f"Bắt đầu khởi tạo {num_nodes} nodes từ {csv_file}...")
for i in range(1, num_nodes + 1):
    init_node_db(i, csv_file)
print("Khởi tạo hoàn tất! Các file db nằm trong thư mục 'nodes/'.")