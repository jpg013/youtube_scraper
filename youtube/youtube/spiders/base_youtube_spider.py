import scrapy
import os
import json
import datetime
from urllib.parse import urlparse

"""BaseYoutubeSpider class is base spider to be inherited from by 
all youtube spiders. This class should never be instantiated
alone, only inherited from."""
class BaseYoutubeSpider(scrapy.Spider):
    name="base_youtube_spider"

    base_url="https://www.youtube.com"

    def __init__(self, *args, **kwargs):
        super(BaseYoutubeSpider, self).__init__(*args, **kwargs)

    def make_channel_about_url(self, channel_id):
        return f"{BASE_YOUTUBE_URL}/channel/{channel_id}/about"

    def get_base_url(self):
        return BaseYoutubeSpider.base_url

    def store_response(self, response, spider):
        obj = self.make_storage_object(response, spider.name)
        key = self.make_storage_key(response.url)
        path = os.path.join('tmp', "youtube", "{}.json".format(key))
        
        with open(path, 'w', encoding="utf8") as outfile:
            json.dump(obj, outfile)
        
        self.log('saved response %s' % path)


    def make_storage_object(self, response, spider_name):
        return {
            "scrape_url": response.url,
            "html_content": response.body_as_unicode(),
            "spider_name": spider_name,
            "crawled_at": datetime.datetime.now().isoformat(),
        }

    def make_storage_key(self, crawl_url):
        now = datetime.datetime.utcnow().isoformat()
        parsed_url = urlparse(crawl_url)
        
        # parse the crawl url into readable file path 
        return "youtube{}_{}".format(parsed_url.path.replace("/", "_"), now)



