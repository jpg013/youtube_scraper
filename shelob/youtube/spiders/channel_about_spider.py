import scrapy
from scrapy import signals
from scrapy.loader import ItemLoader
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers.parse_channel_about as parsers
from youtube.items import AboutChannelItem

class ChannelAboutSpider(BaseYoutubeSpider):
    name="youtube_channel_about_spider"

    def __init__(self, spider_id=None, *args, **kwargs):
        if spider_id is None:
            raise Exception("spider_id arg must be defined")

        self.spider_id = spider_id
        
        super(ChannelAboutSpider, self).__init__(spider_id, *args, **kwargs)
        
        self.parse_args(**kwargs)

        if self.channel_id is None:
            raise Exception("channel_id arg must be defined")

        # dictionary holding spider results
        self.spider_results = {}

    def parse_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == "channel_id":
                self.channel_id = value

    def start_requests(self):
        url = self.make_channel_about_url(self.channel_id)
        
        print("IN THE START REQUESTS", url)
        yield scrapy.Request(
            url=url, 
            callback=self.handle_response,
            errback=self.handle_error
        )

    def parse_data(self, response):
        l = ItemLoader(item=AboutChannelItem(), response=response)
        l.add_css("location", ".country-inline::text")
        l.add_xpath("description", "//div[contains(@class,'about-description')]/pre/text()")
        l.add_xpath("banner_url", "//div[contains(@id,'gh-banner')]/style/text()")
        l.add_css("subscriber_count", ".yt-subscription-button-subscriber-count-branded-horizontal::text")
        l.add_css("is_verified", ".qualified-channel-title.has-badge")
        l.add_xpath("joined_at", "//div[contains(@class, 'about-stats')]/span[2]/text()")
        l.add_xpath("view_count", "//div[contains(@class, 'about-stats')]/span/b/text()")
        l.add_xpath("user_name", "//a[contains(@class, 'channel-header-profile-image-container')]/@href")
        l.add_xpath("screen_name", "//a[contains(@class, 'channel-header-profile-image-container')]/img/@title")
        l.add_xpath("profile_image", "//a[contains(@class, 'channel-header-profile-image-container')]/img/@src")

        for link in parsers.parse_channel_about_links(response):
            l.add_value("links", link)

        return l.load_item()

    def handle_response(self, response):
        print("Handle response??")
        self.store_response(response, self.spider_id)

        print(response.text)

        file = open("channel_about.html", "w")
        file.write(response.text) 
        file.close()

        # data = self.parse_data(response)
        # print(data)
        
        # self.spider_results = dict(self.parse_data(response))
        # print(self.spider_results)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ChannelAboutSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        print("SPIDER IS GETTING CLOSED")

        self.store_spider_results(self.spider_results)
