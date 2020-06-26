import os, sys, json, datetime
import os
import sys
import shutil
from twisted.internet import reactor
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
from shelob.task_queue import TaskQueue
from shelob.config import AppConfig
from logging import getLogger
import uuid
import requests
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

    def update_task_object(self, task_id):
        dir_path = "tmp/{}".format(task_id)
        for f in os.listdir(dir_path):
            file_name = os.path.join(dir_path, f)
            object_name = "{}/{}".format(task_id, f)
            try:
                self.s3_client.upload_file(file_name, self.s3_bucket, object_name)
                logger.info("successfully uploaded results to {} for crawler \"{}\"".format(
                    object_name,
                    task_id
                ))
            except Exception as e:
                logger.error("Error uploading results to S3 for crawler: \"{}\": {}".format(
                    task_id,
                    e
                ))
    
    def create_task_object(self, task_id, crawler_name):
        body = json.dumps({
            "status": "in-progress",
            "id": task_id,
            "name": crawler_name,
        })
        object_name = "{}/{}".format(task_id, "results.json")
        self.s3_client.put_object(
            Body=body,
            Bucket=self.s3_bucket, 
            Key=object_name,
        )

    def schedule_crawl_task(self, crawler_name, task_id, **kwargs):
        try:
            self.task_queue.add_task(crawler_name, task_id, **kwargs)
        except Queue.Full:
            print("Queue is full")
            return None

    def fire_callback(self, url, data):
        headers = {'content-type': 'application/json'}
        requests.post(url, json=data, headers=headers)

    def cleanup_task(self, task_id):
        # remove the directory containg temp files
        dir_path = "tmp/{}".format(task_id)

        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def crawl_by_process(self, crawler_name, task_id, **kwargs):
        self.create_task_object(task_id, crawler_name)
        logger.info("starting crawler \"%s\" with id \"%s\" and args %s", crawler_name, task_id, repr(kwargs))
        cmd = ["python3", "shelob/crawler.py", crawler_name, task_id, json.dumps(kwargs)]
        process = subprocess.run(cmd)

        if process.returncode != 0:
            logger.error("error running crawler \"%s\" with id \"%s\" and args %s", crawler_name, task_id, repr(kwargs))
            return
        
        try:
            # upload results to storage object
            self.update_task_object(task_id)
        finally:
            self.cleanup_task(task_id)
        