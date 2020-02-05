import scrapy
from scrapy import signals
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers.parse_channel_subscriber as parsers
from scrapy.loader import ItemLoader
from youtube.items import ChannelSubscriberItem
import json
import datetime
import urllib.parse

# python3 youtube/crawler.py crawl_channel_subsriber UCXX1iQGufHujuIvQ38MPKMA

class ChannelSubscriberSpider(BaseYoutubeSpider):
    # Spider Name
    name="youtube_channel_subscriber_spider"

    # Max number of crawls spider is allowed to make
    max_crawl_count=10

    # default number of subscribers to crawl
    default_limit = 100

    def __init__(self, spider_id=None, *args, **kwargs):
        super(ChannelSubscriberSpider, self).__init__(*args, **kwargs)      
        
        if spider_id is None:
            raise Exception("spider_id arg must be defined")

        self.spider_id = spider_id

        self.parse_args(**kwargs)
        
        if self.channel_id is None:
            raise Exception("channel_id arg must be defined")
        
        if self.limit is None:
            self.limit = ChannelSubscriberSpider.default_limit

        self.spider_results = {
            "spider_name": ChannelSubscriberSpider.name,
            "youtube_channel_id": self.channel_id,
            "spider_limit": self.limit,
            "spider_id": self.spider_id,
            "results": []
        }
        self.crawl_count = 0
        self.make_response_dir(self.spider_id)
    
    def parse_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == "channel_id":
                self.channel_id = value
            elif key == "limit":
                self.limit = value

    def start_requests(self):
        url = self.make_start_crawl_url()
        return self.do_crawl(url)
        
    def parse_subscriber_item(self, sel):
        """parses and return ChannelSubscriberItem from item selector"""
        l = ItemLoader(item=ChannelSubscriberItem(), selector=sel)
        l.add_xpath("channel_id", "(.//a)[1]/@href")
        l.add_xpath("name", "(.//a)[2]/text()")
        l.add_xpath("subscriber_count", ".//span[contains(@class,'yt-subscription-button-subscriber-count-unbranded-horizontal')]/text()")
        return l.load_item()

    def parse_results(self, resp):
        """Parse the crawl response"""
        content_sel = resp
        load_more_sel = resp
        url_parts = urllib.parse.parse_qs(resp.url)
        is_continuation = "continuation" in url_parts

        if is_continuation:
            # load the response json into a dictionary
            jsonresponse = json.loads(resp.body_as_unicode())
            load_more_sel =  Selector(text=jsonresponse.get("load_more_widget_html"))
            content_sel = Selector(text=jsonresponse.get("content_html"))
        
        results = {}
        results["crawled_at"] = datetime.datetime.utcnow().isoformat()
        results["url"] = resp.url
        results["data"] = []
        results["count"] = 0
        results["next_url"] = parsers.parse_subscriber_load_more(load_more_sel)

        # enumerate over each subscriber content and parse into data item
        for idx, item in enumerate(parsers.parse_subscriber_content_items(content_sel)):
            data = self.parse_subscriber_item(item)
            results["data"].append(dict(data))
            results["count"] += 1

        # append the results dictionary to the spider crawl results
        self.spider_results["results"].append(results)

    def do_crawl(self, crawl_url):
        if self.crawl_count > ChannelSubscriberSpider.max_crawl_count:
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
            "view": "56",
            "flow": "grid"
        }
        
        return "{}/channel/{}/channels?{}".format(
            base_url,
            self.channel_id,
            urllib.parse.urlencode(params)
        )

    def handle_response(self, resp):
        print(resp.request.headers)
        print(resp.request)
        try:
            self.store_response(resp, ChannelSubscriberSpider)
            self.parse_results(resp)
            return self.crawl_next()
            
        except Exception as e:
            print(e)

    def crawl_next(self):
        # have we exceeded result limit
        if self.get_total_results() >= self.limit:
            return
        
        # have we exceeded the max allowed crawl count
        if self.crawl_count > ChannelSubscriberSpider.max_crawl_count:
            return
        
        # do we have any results
        if len(self.spider_results["results"]) == 0:
            return
        
        # get the next_url property from the previous crawled result
        previous_result = self.spider_results["results"][-1]
        next_url = previous_result["next_url"] if previous_result is not None else None
        
        # check if next_url exists
        if next_url is None:
            return
        
        # call do_crawl and return generator
        crawl_url = "{}{}".format(self.get_base_url(), next_url)

        return self.do_crawl(crawl_url)

    def get_total_results(self):
        total = 0
        
        for res_obj in self.spider_results["results"]:
            total += res_obj["count"]
        
        return total

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ChannelSubscriberSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("SPIDER IS GETTING CLOSED")

        self.store_spider_results(self.spider_results, ChannelSubscriberSpider)