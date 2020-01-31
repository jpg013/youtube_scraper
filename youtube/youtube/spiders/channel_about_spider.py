import scrapy
from scrapy.loader import ItemLoader
import os
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers.parse_channel_about as parsers
from youtube.items import AboutChannelItem

class ChannelAboutSpider(BaseYoutubeSpider):
    name="youtube_channel_about_spider"

    def __init__(self, channel_ids, *args, **kwargs):
        if channel_ids is None:
            raise Exception("channel_ids arg must be defined")

        if len(channel_ids) == 0:
            raise Exception("channel_ids must have at least one item")    
        
        super(ChannelAboutSpider, self).__init__(*args, **kwargs)

        # map channel ids to start urls
        self.start_urls = list(map(self.make_channel_about_url, channel_ids))

    def start_requests(self):
        for url in self.start_urls:
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
        self.store_response(response)
        data = self.parse_data(response)
        
        print(data)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    def closed(self, reason):
        print(reason)
