import scrapy
from scrapy import signals
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers.parse_channel_video as parsers
from collections import ChainMap
from scrapy.loader import ItemLoader
from youtube.items import ChannelVideoItem
import json
import datetime
import time
import urllib.parse

class ChannelVideoSpider(BaseYoutubeSpider):
    # Spider Name
    name="youtube_channel_video_spider"

    # Max number of crawls spider is allowed to make
    max_crawl_count=10

    # Sort Options for channel video list
    sort_options={
        "popular": "p",
        "oldest": "da",
        "newest": "dd"
    }

    def __init__(self, channel_id=None, sort=None, limit=100, *args, **kwargs):
        if channel_id is None:
            raise Exception("channel_id arg must be defined")

        super(ChannelVideoSpider, self).__init__(*args, **kwargs)

        # parse the sort option
        self.sort = sort
        self.limit = limit;
        self.channel_id = channel_id
        self.results = []
        self.crawl_count = 0

    def get_sort_option(self):
        """Sets the sort option by given key or default"""
        sort_opts = ChannelVideoSpider.sort_options
        default_sort = sort_opts["newest"]
        return sort_opts.get(self.sort, default_sort)

    def start_requests(self):
        url = self.make_start_crawl_url()

        return self.do_crawl(url)
        
    def parse_video(self, sel):
        """scrapes ChannelVideoItem and returns dictionary item"""
        l = ItemLoader(item=ChannelVideoItem(), selector=sel)
        l.add_xpath("id", "./div[contains(@class,'yt-lockup-video')]/@data-context-item-id")
        l.add_xpath("view_count", ".//ul[contains(@class,'yt-lockup-meta-info')]/li[1]/text()")
        l.add_xpath("duration", ".//span[contains(@class,'video-time')]/span/text()")
        l.add_xpath("thumbnail", ".//img/@src")
        l.add_xpath("created_at", ".//ul[contains(@class,'yt-lockup-meta-info')]/li[2]/text()")
        return l.load_item()
    
    def parse_results(self, resp):
        """Parse the video list response"""
        url_parts = urllib.parse.parse_qs(resp.url)
        is_continuation = "continuation" in url_parts
        video_results = {}
        video_results["crawled_at"] = datetime.datetime.now().isoformat()
        video_results["url"] = resp.url
        video_results["data"] = []
        
        next_url = parsers.parse_continuation_url(resp) if is_continuation else parsers.parse_next_url(resp)
        print("NEXT URL", next_url)
        
        video_results["next_url"] = next_url

        links = parsers.parse_channel_video_continuation_links(resp) if is_continuation else parsers.parse_channel_video_links(resp)


        for idx, item in enumerate(links):
            video_results["data"].append(self.parse_video(item))
        
        video_results["video_count"] = len(video_results["data"])
        self.results.append(video_results)

    def do_crawl(self, crawl_url):
        if self.crawl_count > ChannelVideoSpider.max_crawl_count:
            raise CloseSpider('max_crawl_count exceeded')
        
        self.crawl_count +=1
        
        yield scrapy.Request(
            url=crawl_url,
            callback=self.handle_response,
            errback=self.handle_error
        )

    def make_start_crawl_url(self,):
        base_url = self.get_base_url()
        params = {
            "view": "0",
            "sort": self.get_sort_option(),
            "flow": "grid"
        }
        
        return "{}/channel/{}/videos?{}".format(
            base_url,
            self.channel_id,
            urllib.parse.urlencode(params)
        )

    def handle_response(self, resp):
        try:
            self.store_response(
                self.make_storage_key(),
                self.make_storage_object(resp)
            )
            self.parse_results(resp)

            next_url = self.get_next_url()

            if next_url is not None:
                # Wait for 3 seconds
                time.sleep(3)
                return self.do_crawl(next_url)
        except Exception as e:
            print(e)

    def get_next_url(self):
        # have we exceeded max count
        if self.get_total_results() >= self.limit:
            return

        if len(self.results) == 0:
            return
        
        last = self.results[-1]
        next_url = last["next_url"] if last is not None else None
        
        if next_url is None:
            print("What the fook are we here??")
            return

        return "{}{}".format(
            self.get_base_url(),
            next_url
        )

    def make_storage_object(self, response):
        return {
            "scrape_url": response.url,
            "html_content": response.body_as_unicode(),
            "spider_name": ChannelVideoSpider.name,
            "crawled_at": datetime.datetime.now().isoformat(),
        }

    def make_storage_key(self):
        try:
            timestamp = int(round(time.time() * 1000))
            return "crawl_youtube_channel_video_{}_{}".format(self.channel_id, timestamp)
        except Exception as e:
            print(e)

    def get_total_results(self):
        total = 0
        
        for res_obj in self.results:
            total += res_obj["video_count"]
        
        return total

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ChannelVideoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("SPIDER IS GETTING CLOSED")
        for result in self.results:
            print(result)
