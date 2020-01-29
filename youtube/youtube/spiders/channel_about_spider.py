import scrapy
import os
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers as parsers
from collections import ChainMap

class ChannelAboutSpider(BaseYoutubeSpider):
    name="youtube_channel_about_spider"

    def __init__(self, channel_ids, *args, **kwargs):
        if channel_ids is None:
            raise Exception("channel_ids arg must be defined")

        if len(channel_ids) == 0:
            raise Exception("channel_ids must have at least one item")    
        
        super(ChannelAboutSpider, self).__init__(*args, **kwargs)

        # pipeline of parsers
        self.parsing_pipeline = [
            parsers.parse_channel_about_name,
            parsers.parse_channel_about_description,
            parsers.parse_channel_about_subscriber_count,
            parsers.parse_channel_about_stats,
            parsers.parse_channel_about_location,
            parsers.parse_channel_about_links
        ]

        # map channel ids to start urls
        self.start_urls = list(map(self.make_channel_about_url, channel_ids))
        print(self.start_urls)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.handle_response,
                errback=self.handle_error
            )

    def parse_results(self, resp):
        results = list(map(lambda x: x(resp), self.parsing_pipeline))
        return dict(ChainMap(*results))

    def handle_response(self, response):
        self.spider_results = self.parse_results(response)
        # parts = response.url.split("/")
        # filename = "youtube_channel_about_%s.html" % parts[4]
        # path = os.path.join('tmp', filename)

        # with open(path, 'wb') as f:
        #     f.write(response.body)
        
        # self.log('Saved file %s' % filename)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    def closed(self, reason):
        print(reason)
