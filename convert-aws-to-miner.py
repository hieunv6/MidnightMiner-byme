import json
import os
from datetime import datetime

# Lấy đường dẫn tuyệt đối đến thư mục keys
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.join(os.path.dirname(script_dir), 'keys_old_2', 'ap-south-1')
result = []

# Đọc từ miner1 đến miner60
for i in range(1, 1000):
    miner_name = f'miner{i}'
    miner_path = os.path.join(base_dir, miner_name)
    
    if not os.path.exists(miner_path):
        print(f"⚠ Không tìm thấy thư mục {miner_name}")
        continue
    
    try:
        miner_data = {}
        
        # Đọc address
        addr_file = os.path.join(miner_path, 'payment.addr')
        if os.path.exists(addr_file):
            with open(addr_file, 'r') as f:
                miner_data['address'] = f.read().strip()
        
        # Đọc skey và lấy cborHex
        skey_file = os.path.join(miner_path, 'payment.skey')
        if os.path.exists(skey_file):
            with open(skey_file, 'r') as f:
                skey = json.load(f)
                # Lấy cborHex từ skey
                if 'cborHex' in skey:
                    miner_data['signing_key'] = skey['cborHex']
        
        if 'address' in miner_data and 'signing_key' in miner_data:
            result.append(miner_data)
            print(f"✓ Đọc thành công {miner_name}")
        else:
            print(f"⚠ {miner_name} thiếu dữ liệu")
        
    except Exception as e:
        print(f"✗ Lỗi khi đọc {miner_name}: {str(e)}")

# Xuất ra JSON
output_json = json.dumps(result, indent=2)
print(f"\n{'='*60}")
print(f"Tổng số miner: {len(result)}")
print(f"{'='*60}\n")
print(output_json)

# Lưu vào file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'payments_output_{timestamp}.json'
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n✓ Đã lưu vào file: {output_file}")