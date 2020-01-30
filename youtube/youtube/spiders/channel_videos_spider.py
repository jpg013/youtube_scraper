import scrapy
import os
from .base_youtube_spider import BaseYoutubeSpider
import youtube.scrapers.scrape_channel_video as scrapers
from collections import ChainMap

class ChannelVideosSpider(BaseYoutubeSpider):
    name="youtube_channel_videos_spider"

    def __init__(self, channel_id, *args, **kwargs):
        if channel_id is None:
            raise Exception("channel_id arg must be defined")

        super(ChannelVideosSpider, self).__init__(*args, **kwargs)

        # pipeline of parsers
        self.scraping_pipeline = [
            scrapers.scrape_channel_video_duration,
            scrapers.scrape_channel_video_id,
            scrapers.scrape_channel_video_meta,
            scrapers.scrape_channel_video_thumbnail
        ]

        # map channel ids to start urls
        self.start_urls = [self.make_channel_videos_url(channel_id)]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.handle_response,
                errback=self.handle_error
            )

    def parse_results(self, resp):
        # Parse the video list response
        spider_results = []
        links = parsers.parse_channel_video_links(resp)
        
        for idx, li_sel in enumerate(links):
            video_results = list(map(lambda x: x(resp), self.parsing_pipeline))
            spider_results.append(dict(ChainMap(*video_results)))

        return spider_results

    def handle_response(self, response):
        try:
            self.spider_results = self.parse_results(response)
            print(self.spider_results)
        except Exception as e:
            print(e)
        # parts = response.url.split("/")
        # filename = "youtube_channel_videos_%s.html" % parts[4]
        # path = os.path.join('tmp', filename)

        # with open(path, 'wb') as f:
        #     f.write(response.body)
        
        # # self.log('Saved file %s' % filename)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    def closed(self, reason):
        print(reason)