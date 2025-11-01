# D:\web-project-docker\sensor_producer.py
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# Kết nối đúng cổng bên ngoài
producer = KafkaProducer(
    bootstrap_servers='localhost:9094',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# SỬA 1: Đổi tên topic
topic_name = 'test-topic'

# Giữ nguyên ID để Spark có thể join
location_ids = ["TEST001", "TEST002", "TEST003"]

print(f"--- Bắt đầu gửi dữ liệu CẢM BIẾN giả lập vào topic '{topic_name}' ---")
print("--- Nhấn Ctrl+C để dừng ---")

try:
    while True:
        selected_location = random.choice(location_ids)

        # SỬA 2: Tạo dữ liệu CẢM BIẾN (khớp với sensor_schema trong Spark)
        sensor_data = {
            "location_id": selected_location,
            "timestamp": datetime.now().isoformat(), # Thời gian hiện tại
            "pm25": round(random.uniform(5.0, 70.0), 1),  # Giá trị PM2.5 ngẫu nhiên
            "pm10": round(random.uniform(10.0, 100.0), 1) # Giá trị PM10 ngẫu nhiên
        }

        # SỬA 3: Gửi vào topic mới
        print(f"Gửi: {sensor_data}")
        producer.send(topic_name, value=sensor_data)
        producer.flush()

        # Gửi thường xuyên hơn một chút
        time.sleep(random.uniform(3, 7))

except KeyboardInterrupt:
    print("\n--- Dừng gửi dữ liệu ---")
finally:
    producer.close()
    print("--- Producer đã đóng ---")