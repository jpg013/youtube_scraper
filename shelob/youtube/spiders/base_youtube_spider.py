import scrapy
import os
import json
import datetime
from urllib.parse import urlparse
from pathlib import Path

"""BaseYoutubeSpider class is base spider to be inherited from by 
all youtube spiders. This class should never be instantiated
alone, only inherited from."""
class BaseYoutubeSpider(scrapy.Spider):
    name="base_youtube_spider"

    base_url="https://www.youtube.com"

    def __init__(self, spider_id=None, *args, **kwargs):
        super(BaseYoutubeSpider, self).__init__(*args, **kwargs)
        self.make_response_dir(spider_id)

    def make_channel_about_url(self, channel_id):
        return f"{self.base_url}/channel/{channel_id}/about"

    def get_base_url(self):
        return BaseYoutubeSpider.base_url

    def make_response_dir(self, object_id):
        self.response_dir = "tmp/{}".format(object_id)
        Path(self.response_dir).mkdir(parents=True, exist_ok=True)

    def store_response(self, response, spider_id):
        obj = self.make_storage_object(response, spider_id)
        key = self.make_storage_key(response.url)
        path = os.path.join(self.response_dir, "{}".format(key))
        
        with open(path, 'w', encoding="utf8") as outfile:
            json.dump(obj, outfile)
        
    def store_spider_results(self, data):
        key = "spider_results.json"
        path = os.path.join(self.response_dir, "{}".format(key))
        
        with open(path, 'w', encoding="utf8") as outfile:
            json.dump(data, outfile)

    def make_storage_object(self, response, spider_id):
        return {
            "scrape_url": response.url,
            "response_content": response.body_as_unicode(),
            "spider_id": spider_id,
            "crawled_at": datetime.datetime.now().isoformat(),
        }

    def make_storage_key(self, crawl_url):
        now = datetime.datetime.utcnow().isoformat()
        parsed_url = urlparse(crawl_url)
        
        # parse the crawl url into readable file path 
        return "youtube{}.{}-json".format(parsed_url.path.replace("/", "-"), now)