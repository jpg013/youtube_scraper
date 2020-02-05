import sys
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
import logging
from scrapy.utils.project import get_project_settings
import youtube.spiders as spiders
import json

# @defer.inlineCallbacks
# def crawl_youtube_channel_about(runner):
#     yield runner.crawl(spiders.ChannelAboutSpider, channel_ids=[sys.argv[2]])
#     reactor.stop()

# @defer.inlineCallbacks
# def crawl_youtube_channel_video(runner):
#     yield runner.crawl(spiders.ChannelVideoSpider, channel_id=sys.argv[2])
#     print("done crawling spider")
#     reactor.stop()

@defer.inlineCallbacks
def crawl_youtube_channel_subscriber(runner, id, crawler_args):
    yield runner.crawl(spiders.ChannelSubscriberSpider, spider_id=id, **crawler_args)
    reactor.stop()

def switch_crawler(name):
    switcher = {
        # "youtube_channel_about": crawl_youtube_channel_about,
        # "youtube_channel_video": crawl_youtube_channel_video,
        "youtube_channel_subscriber": crawl_youtube_channel_subscriber,
    }

    return switcher.get(name, "invalid crawler")

def main():
    crawler_name = sys.argv[1]
    crawler_id = sys.argv[2]
    crawler_args = json.loads(sys.argv[3])
    
    crawl_func = switch_crawler(crawler_name)
    
    if crawl_func == "invalid crawler":
        print("invalid crawler")
        return
    
    runner = CrawlerRunner(get_project_settings())
    crawl_func(runner, crawler_id, crawler_args)
    reactor.run()

if __name__ == "__main__":
    main()
