const CONTROLLER = 'http://127.0.0.1:5000';
const NODES = {
    1: 'http://127.0.0.1:5001',
    2: 'http://127.0.0.1:5002',
    3: 'http://127.0.0.1:5003',
    4: 'http://127.0.0.1:5004',
    5: 'http://127.0.0.1:5005'
};

function printLog(msg) {
    const box = document.getElementById('consoleLog');
    box.innerHTML += `<br>[${new Date().toLocaleTimeString()}] ${msg}`;
    box.scrollTop = box.scrollHeight;
}

async function fetchClusterData() {
    const pId = document.getElementById('prodIdInput').value.trim();
    printLog(`Đang quét trạng thái tồn kho cho mã sản phẩm: ${pId}...`);

    for (let i = 1; i <= 5; i++) {
        try {
            let res = await fetch(`${NODES[i]}/get/${pId}`);
            if (res.ok) {
                let data = await res.json();
                document.getElementById(`stock${i}`).innerText = data.stock;
            } else {
                document.getElementById(`stock${i}`).innerText = 'LỖI';
            }
        } catch (e) {
            document.getElementById(`stock${i}`).innerText = 'DOWN';
        }
    }

    try {
        let netRes = await fetch(`${CONTROLLER}/status`);
        let netData = await netRes.json();
        const banner = document.getElementById('netStatus');

        if (netData.is_partitioned) {
            banner.className = "network-banner partitioned";
            banner.innerText = "CẢNH BÁO: MẠNG BỊ PHÂN MẢNH (Split-Brain) | Khối {1,2} và Khối {3,4,5} bị cô lập";
        } else {
            banner.className = "network-banner normal";
            banner.innerText = "TRẠNG THÁI HỆ THỐNG: BÌNH THƯỜNG (Mạng Toàn Vẹn - 5 Nodes Đồng Bộ)";
        }
    } catch (e) {
        printLog(`<span style="color: #ef4444;">Không thể kết nối đến Network Controller!</span>`);
    }
}

async function triggerPartition() {
    try {
        await fetch(`${CONTROLLER}/partition`, { method: 'POST' });
        printLog(`<span style="color: #fb923c;">Thực thi lệnh cô lập kết nối mạng. Hệ thống chính thức rơi vào trạng thái lỗi Split-Brain.</span>`);
        await fetchClusterData();
    } catch (e) {
        printLog(`<span style="color: #ef4444;">Lỗi: Không thể kết nối Controller để ngắt mạng!</span>`);
    }
}

async function triggerHeal() {
    printLog("Đang kích hoạt khôi phục hệ thống và hội tụ dữ liệu toàn cluster...");
    try {
        let res = await fetch(`${CONTROLLER}/heal`, { method: 'POST' });

        if (res.ok) {
            isPartitioned = false;

            const netStatus = document.getElementById('netStatus');
            netStatus.className = "network-banner normal";
            netStatus.innerText = "TRẠNG THÁI HỆ THỐNG: BÌNH THƯỜNG (Mạng Toàn Vẹn - 5 Nodes Đồng Bộ)";

            printLog("<span style='color: #10b981;'>[THÀNH CÔNG] Toàn bộ mạng lưới đã được chữa lành và đồng bộ tất cả sản phẩm!</span>");
        } else {
            printLog("<span style='color: #ef4444;'>[THẤT BẠI] Controller trả về lỗi khi khôi phục mạng.</span>");
        }
    } catch (e) {
        printLog("<span style='color: #ef4444;'>Lỗi kết nối đến Controller khi thực hiện lệnh Heal!</span>");
    }
    await fetchClusterData();
}

async function executeWrite(targetNode, amount) {

    let startTime = performance.now();

    const pId = document.getElementById('prodIdInput').value.trim();

    let currentStock = NaN;
    for (let i = 1; i <= 5; i++) {
        let val = parseInt(document.getElementById(`stock${i}`).innerText);
        if (!isNaN(val)) {
            currentStock = val;
            break;
        }
    }

    if (isNaN(currentStock)) {
        alert("Toàn bộ hệ thống đã sập, không thể đọc được dữ liệu gốc!");
        return;
    }

    let newStock = currentStock - amount;
    printLog(`[WRITE] Khởi tạo giao dịch cập nhật kho hàng: ${currentStock} -> ${newStock}`);

    let isPartitioned = false;
    try {
        let netRes = await fetch(`${CONTROLLER}/status`);
        let netData = await netRes.json();
        isPartitioned = netData.is_partitioned;
    } catch (e) {
        printLog(`<span style="color: #ef4444;"> Lỗi: Không thể lấy trạng thái mạng từ Controller!</span>`);
        return;
    }

    let affectedNodes = [];
    if (!isPartitioned) {
        affectedNodes = [1, 2, 3, 4, 5];
    } else {
        affectedNodes = (targetNode === 1) ? [1, 2] : [3, 4, 5];
    }

    for (let node of affectedNodes) {
        try {
            let res = await fetch(`${NODES[node]}/set/${pId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stock: newStock })
            });

            if (!res.ok) {
                let errorData = await res.json();
                printLog(`<span style="color: #ef4444;"> [TỪ CHỐI GHI] Node ${node} báo lỗi: ${errorData.error}</span>`);
            } else {
                printLog(` -> Đã ghi dữ liệu thành công xuống tập tin sqlite cục bộ của Node ${node}`);
            }

        } catch (e) {
            printLog(`<span style="color: #ef4444;"> -> Lỗi kết nối đến Node ${node} (Node có thể đã sập)</span>`);
        }
    }
    await fetchClusterData();

    let endTime = performance.now();
    let latency = Math.round(endTime - startTime);

    document.getElementById("latencyDisplay").innerText = latency + " ms";
    printLog(`<strong> [METRICS] Độ trễ giao dịch (Latency): <span style="color: #fbbf24;">${latency} ms</span></strong>`);
}

fetchClusterData();