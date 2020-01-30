import scrapy
import os
from .base_youtube_spider import BaseYoutubeSpider
import youtube.scrapers.scrape_channel_about as scrapers
from collections import ChainMap

class ChannelAboutSpider(BaseYoutubeSpider):
    name="youtube_channel_about_spider"

    def __init__(self, channel_ids, *args, **kwargs):
        if channel_ids is None:
            raise Exception("channel_ids arg must be defined")

        if len(channel_ids) == 0:
            raise Exception("channel_ids must have at least one item")    
        
        super(ChannelAboutSpider, self).__init__(*args, **kwargs)

        # list of scrapers
        self.scraping_pipeline = [
            scrapers.scrape_channel_about_name,
            scrapers.scrape_channel_about_description,
            scrapers.scrape_channel_about_subscriber_count,
            scrapers.scrape_channel_about_stats,
            scrapers.scrape_channel_about_location,
            scrapers.scrape_channel_about_links,
            scrapers.scrape_channel_about_banner,
            scrapers.scrape_channel_about_is_verified,
        ]

        # map channel ids to start urls
        self.start_urls = list(map(self.make_channel_about_url, channel_ids))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.handle_response,
                errback=self.handle_error
            )

    def scrape_results(self, resp):
        results = list(map(lambda x: x(resp), self.scraping_pipeline))
        self.results = dict(ChainMap(*results))

    def handle_response(self, response):
        self.store_response(response)
        self.scrape_results(response)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    def closed(self, reason):
        print(reason)
