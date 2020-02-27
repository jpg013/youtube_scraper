from logging  import getLogger, Formatter, StreamHandler, DEBUG, INFO
import socket, sys
from datetime import datetime
import json
from shelob.kafka import kafka_producer
from shelob.config import AppConfig

class LogFormatter(Formatter):
    fields=[
        "traceId",
        "id",
        "parentId",
        "timestamp",
        "hostname",
        "type",
        "facility",
        "severity",
        "namespace",
        "component",
        "version",
        "message",
        "stackTrace",
        "lineNumber",
        "httpMethod",
        "httpRoute",
        "parameters",
        "httpResponseCode",
        "filename",
        "duration",
        "environment",
        "subenvironment",
        "buildNumber",
    ]

    def __init__(self):
        self.__default_values = {
            "hostname": socket.gethostname(),
            "environment": AppConfig.ENVIRONMENT,
            "sub_environment": AppConfig.SUB_ENVIRONMENT,
            "component": AppConfig.COMPONENT,
            "namespace": AppConfig.NAMESPACE,
            "version": AppConfig.VERSION,
            "buildNumber": AppConfig.BUILD_NUMBER
        }

    @property
    def default_values(self):
        return self.__default_values
    
    @default_values.setter
    def default_values(self, key, val):
        if key not in self.fields:
            return

        self.__default_values[key] = val

    def format(self, record):
        log_message = {
            'timestamp': datetime.utcnow().isoformat(),
            'hostname': socket.gethostname(),
            'severity': record.levelname.lower(),
            'lineNumber': record.lineno,
            'filename': record.filename,
            'message': record.getMessage()
        }
        
        if self.__default_values:
            log_message.update(self.__default_values)
        
        if hasattr(record, 'props'):
            log_message.update(record.props)

        if record.exc_info:
            log_message['stackTrace'] = self.formatException(record.exc_info)
        elif record.stack_info:
            log_message['stackTrace'] = record.stack_info
        elif record.exc_text:
            log_message['stackTrace'] = record.exc_text

        return log_message

class StdOutFormatter(LogFormatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        log_message = super().format(record)
        return json.dumps(log_message)

class KafkaHandler(StreamHandler):
    def __init__(self, topic="app_log"):
        if kafka_producer is None:
            raise ValueError('kafka_producer not provided to kafka logger.')
        
        StreamHandler.__init__(self)
        self.kafka_producer = kafka_producer
        self.topic = topic

    def emit(self, record):
        payload = self.format(record)
        self.kafka_producer.publish(self.topic, payload)

class LogProvider():
    def stdout_handler(self):
        stdoutHandler = StreamHandler(sys.stdout)
        stdoutHandler.setLevel(DEBUG)
        stdoutHandler.setFormatter(StdOutFormatter())
        return stdoutHandler

    def kafka_handler(self):
        kafka_handler = KafkaHandler()
        kafka_handler.setFormatter(LogFormatter())
        kafka_handler.setLevel(INFO)
        return kafka_handler
    
    def config_logger(self, app_name):
        logger = getLogger(app_name)
            
        # if testing exit early
        if AppConfig.TESTING is True:
            return logger

        if AppConfig.DEBUG is True:
            logger.setLevel(DEBUG)
            logger.addHandler(self.stdout_handler())
            return logger

        # set production level to info and add kafka handler
        logger.setLevel(INFO)
        logger.addHandler(self.kafka_handler())

        return logger

log_provider = LogProvider()