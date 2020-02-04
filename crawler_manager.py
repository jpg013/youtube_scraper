import os, sys, json, datetime
from twisted.internet import reactor
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
from task_pool import TaskPool

class CrawlerManager():
    def __init__(self, config):
        self.s3_access_key_id = config.get("S3_ACCESS_KEY_ID", "")
        self.s3_bucket = config.get("S3_BUCKET", "")
        self.s3_secret_access_key = config.get("S3_SECRET_ACCESS_KEY", "")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.s3_access_key_id,
            aws_secret_access_key=self.s3_secret_access_key
        )
        self.task_pool = TaskPool(
            10, # 10 task workers,
            self.crawl_by_process,
            self.upload_results_to_s3,
        )
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
        now = datetime.datetime.now().isoformat()
        return "{}_{}".format(crawler_name, now)

    def upload_results_to_s3(self, crawler_id):
        dir_path = "tmp/{}".format(crawler_id)

        for f in os.listdir(dir_path):
            file_name = os.path.join(dir_path, f)
            object_name = "{}/{}".format(crawler_id, f)
            print("storing file", file_name)
            print("object", object_name)
            try:
                self.s3_client.upload_file(file_name, self.s3_bucket, object_name)
            except Exception as e:
                print(e)

    def schedule_crawl_task(self, crawler_name, args):
        try:
            crawler_id = self.generate_crawler_id(crawler_name)
            self.task_pool.add_task(crawler_id, crawler_name, args)
            return crawler_id    
        except Queue.Full:
            print("Queue is full")
            return None

    def crawl_by_process(self, crawler_id, crawler_name, args):
        print("in the crawl by process")
        print(crawler_name)
        print(crawler_id)
        print(args)
        # print(args)
        # crawler_id = self.generate_crawler_id(crawler_name)
        # cmd = ["python3", "youtube/crawler.py", crawler_name, crawler_id,  json.dumps(crawl_args)]
        # process = subprocess.run(cmd)

        # if process.returncode == 0:
        #     self.upload_results_to_s3(crawler_id)
        # else:
        #     print("FAILURE")
        