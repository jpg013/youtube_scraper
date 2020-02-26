"""Application Config"""
from shelob import __version__, __build_number__, __component__, __namespace__
import os

ENVIRONMENT=os.getenv('APP_ENVIRONMENT', 'nonprod')
SUB_ENVIRONMENT=os.getenv('APP_SUBENVIRONMENT', 'debug')

class AppConfig(object):
    VERSION = __version__
    BUILD_NUMBER = __build_number__
    COMPONENT = __component__
    NAMESPACE = __namespace__
    ENVIRONMENT=ENVIRONMENT
    SUB_ENVIRONMENT=SUB_ENVIRONMENT
    DEBUG=True if SUB_ENVIRONMENT == "debug" else False
    TESTING=True if ENVIRONMENT == "test" else False
    TASK_WORKER_COUNT=10 # number of worker threads running
    QUEUE_MAX_SIZE=1000 # max number of items that can be stored in the queue
    APPLICATION_NAME="shelob"
    S3_ACCESS_KEY_ID="AKIAIWI5KF57TEG4Q3CA"
    S3_SECRET_ACCESS_KEY="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"
    S3_BUCKET="dunami-reporting-nonprod"
    KAFKA_HOST="xnd-kafka-data00.aws.dunami.com:9092,xnd-kafka-data01.aws.dunami.com:9092,xnd-kafka-data02.aws.dunami.com:9092"
    
    @staticmethod
    def LOG_LEVEL(self):
        if self.DEBUG is True:
            return "DEBUG"

        return "INFO"
    
    @staticmethod
    def get_dict():
        return {
            "version": AppConfig.VERSION,
            "build_number": AppConfig.BUILD_NUMBER,
            "component": AppConfig.COMPONENT,
            "namespace": AppConfig.NAMESPACE,
            "environment": AppConfig.ENVIRONMENT,
            "sub_environment": AppConfig.SUB_ENVIRONMENT,
            "consul_host": AppConfig.CONSUL_HOST,
            "debug": AppConfig.DEBUG,
            "testing": AppConfig.TESTING,
            "kafka_host": AppConfig.KAFKA_HOST,
            "task_worker_count": AppConfig.TASK_WORKER_COUNT,
            "queue_max_size": AppConfig.QUEUE_MAX_SIZE,
            "application_name": AppConfig.APPLICATION_NAME,
            "s3_access_key_id": AppConfig.S3_ACCESS_KEY_ID,
            "s3_secret_access_key": AppConfig.S3_SECRET_ACCESS_KEY,
            "s3_bucket": AppConfig.S3_BUCKET,
        }