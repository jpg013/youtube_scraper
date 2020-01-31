import scrapy
from scrapy.selector import Selector
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

    # Sort Options for channel video list
    sort_options={
        "popular": "p",
        "oldest": "da",
        "newest": "dd"
    }

    def __init__(self, channel_id=None, sort=None, scrape_count=50, *args, **kwargs):
        if channel_id is None:
            raise Exception("channel_id arg must be defined")

        super(ChannelVideoSpider, self).__init__(*args, **kwargs)

        # parse the sort option
        self.set_sort_option(sort)
        self.scrape_count = scrape_count;
        self.channel_id = channel_id

        # map channel ids to start urls
        self.start_urls = [
            self.make_channel_video_url(channel_id, self.sort_option)
        ]

        self.results = []

    def set_sort_option(self, sort_key):
        """Sets the sort option by given key or default"""
        sort_opts = ChannelVideoSpider.sort_options
        default_sort = sort_opts["newest"]
        self.sort_option = sort_opts.get(sort_key, default_sort)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.handle_response,
                errback=self.handle_error
            )

    def parse_next_response(self, response):
        pass
        # # Parse the html content into a selector
        # jsonresponse = json.loads(response.body_as_unicode())
        # sel = Selector(text=jsonresponse.get("content_html"))
        
        # links = parsers.parse_channel_video_more_links(sel)
        # print(len(links))

        # for idx, li_sel in enumerate(links):
        #     l = ItemLoader(item=ChannelVideoItem(), selector=li_sel)
        #     l.add_xpath("id", "./div[contains(@class,'yt-lockup-video')]/@data-context-item-id")
        #     l.add_xpath("view_count", ".//ul[contains(@class,'yt-lockup-meta-info')]/li[1]/text()")
        #     l.add_xpath("duration", ".//span[contains(@class,'video-time')]/span/text()")
        #     l.add_xpath("thumbnail", ".//img/@src")
        #     l.add_xpath("created_at", ".//ul[contains(@class,'yt-lockup-meta-info')]/li[2]/text()")
        #     x = l.load_item()
        #     print(x)

    def crawl_next(self):
        print("crawl_next")
        print("total results", self.get_total_results())
        print("scrape count", self.scrape_count)
        
        # have we exceeded max count
        if self.get_total_results() >= self.scrape_count:
            return

        next_url = self.get_next_url()
        
        if next_url is None:
            print("We do not hav a next url")
            return

        print("Fetching from: ", next_url)
        
        yield scrapy.Request(
            url="https://www.youtube.com" + next_url,
            callback=self.handle_response,
            errback=self.handle_error
        )

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
        video_results["next_url"] = parsers.parse_next_url(resp)

        links = []

        if is_continuation:
            jsonresponse = json.loads(resp.body_as_unicode())
            sel = Selector(text=jsonresponse.get("content_html"))
            links = parsers.parse_channel_video_continuation_links(sel)
        else:
            links = parsers.parse_channel_video_links(resp)

        for idx, item in enumerate(links):
            video_results["data"].append(self.parse_video(item))
        
        video_results["video_count"] = len(video_results["data"])
        self.results.append(video_results)

    def handle_response(self, resp):
        try:
            self.store_response(
                self.make_storage_key(),
                self.make_storage_object(resp)
            )
            self.parse_results(resp)

            return self.crawl_next()
        except Exception as e:
            print(e)

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

    def get_next_url(self):
        if len(self.results) == 0:
            return
        
        last = self.results[-1]

        if last is not None:
            return last["next_url"]

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)