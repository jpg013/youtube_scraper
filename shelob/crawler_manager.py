import os, sys, json, datetime
from twisted.internet import reactor
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
from shelob.task_queue import TaskQueue
from shelob.config import AppConfig
from logging import getLogger
import uuid
from enum import Enum

logger = getLogger("shelob.crawler_manager")

class CrawlerManager():
    def __init__(self):
        self.s3_access_key_id = AppConfig.S3_ACCESS_KEY_ID
        self.s3_bucket = AppConfig.S3_BUCKET
        self.s3_secret_access_key = AppConfig.S3_SECRET_ACCESS_KEY
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.s3_access_key_id,
            aws_secret_access_key=self.s3_secret_access_key
        )
        self.task_queue = TaskQueue(
            max_size=1000,
            worker_count=10,
            do_task=self.crawl_by_process,
            result_handler=self.upload_results_to_s3,
        )
        self.task_queue.run()

    def spider_closing(self):
        """Activates on spider closed signal"""
        print("Closing reactor")
        reactor.stop()
        pass
    
    def start_reactor(self):
        if not reactor.running:
            try:
                reactor.run()
            except:
                pass

    def stop_reactor(self):
        if reactor.running:
            reactor.stop()

    def generate_crawler_id(self, crawler_name):
        return "{}_{}".format(crawler_name, uuid.uuid4())

    def upload_results_to_s3(self, crawler_id):
        dir_path = "tmp/{}".format(crawler_id)
        for f in os.listdir(dir_path):
            file_name = os.path.join(dir_path, f)
            object_name = "{}/{}".format(crawler_id, f)
            try:
                self.s3_client.upload_file(file_name, self.s3_bucket, object_name)
                logger.info("successfully uploaded results to {} for crawler \"{}\"".format(
                    object_name,
                    crawler_id
                ))
            except Exception as e:
                logger.error("Error uploading results to S3 for crawler: \"{}\": {}".format(
                    crawler_id,
                    e
                ))

    def schedule_crawl_task(self, crawler_name, crawler_args):
        try:
            crawler_id = self.generate_crawler_id(crawler_name)
            self.task_queue.add_task(crawler_name, crawler_id, crawler_args)
            return crawler_id
        except Queue.Full:
            print("Queue is full")
            return None

    def crawl_by_process(self, crawler_name, crawler_id, *args):
        logger.info("starting crawler \"%s\" with id \"%s\" and args %s", crawler_name, crawler_id, repr(args))
        cmd = ["python3", "shelob/crawler.py", crawler_name, crawler_id,  json.dumps(*args)]
        process = subprocess.run(cmd)

        if process.returncode != 0:
            logger.error("error running crawler \"%s\" with id \"%s\" and args %s", crawler_name, crawler_id, repr(args))
            return

        # Return the crawler_id to the calling thread
        return crawler_id
        