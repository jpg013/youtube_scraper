from kafka import KafkaProducer
from shelob.config import AppConfig
import json

class Producer():
    def __init__(self):
        self.producer = None

    def connect(self):
        self.producer = KafkaProducer(
            bootstrap_servers=AppConfig.KAFKA_HOST, 
            client_id="shelob", 
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )

    def publish(self, topic, msg):
        if self.producer is None:
            self.connect()
        
        self.producer.send(topic, msg)

kafka_producer = Producer()
