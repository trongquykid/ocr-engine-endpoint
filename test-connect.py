import requests
import json

# Địa chỉ Kafka Connect REST API
kafka_connect_url = "http://localhost:8083/connectors"

# Cấu hình MongoDB Source Connector
connector_config = {
    "name": "mongo-source-connector",
    "config": {
        "connector.class": "com.mongodb.kafka.connect.MongoSourceConnector",
        "tasks.max": "1",
        "connection.uri": "mongodb://localhost:27017",
        "database": "ocr-system",
        "collection": "test",
        "topic.prefix": "test",
        "output.format.value": "json",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter"
    }
}

# Gửi request POST để tạo connector
response = requests.post(kafka_connect_url, headers={"Content-Type": "application/json"},
                         data=json.dumps(connector_config))

# Kiểm tra phản hồi từ server
if response.status_code == 201:
    print("Connector created successfully!")
else:
    print(f"Failed to create connector: {response.text}")