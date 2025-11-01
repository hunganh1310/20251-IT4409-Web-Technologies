import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# Cấu hình Kafka producer (kết nối tới port 9094 trên máy host)
producer = KafkaProducer(
    bootstrap_servers='localhost:9094', # <--- SỬA THÀNH CỔNG BÊN NGOÀI 9094
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

location_ids = ["TEST001", "TEST002", "TEST003"]
print("--- Bắt đầu gửi dữ liệu thời tiết giả lập vào topic 'weather-raw' ---")
print("--- Nhấn Ctrl+C để dừng ---")

try:
    while True:
        selected_location = random.choice(location_ids)
        weather_data = {
            "weather_location_id": selected_location,
            "weather_time": datetime.now().isoformat(),
            "temperature": round(random.uniform(15.0, 35.0), 1),
            "humidity": round(random.uniform(40.0, 90.0), 1),
            "wind_speed": round(random.uniform(0.0, 15.0), 1)
        }
        print(f"Gửi: {weather_data}")
        producer.send('weather-raw', value=weather_data)
        producer.flush()
        time.sleep(random.uniform(5, 10))

except KeyboardInterrupt:
    print("\n--- Dừng gửi dữ liệu ---")
finally:
    producer.close()
    print("--- Producer đã đóng ---")

