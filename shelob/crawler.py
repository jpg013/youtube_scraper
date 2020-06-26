import sys
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
import logging
from scrapy.utils.project import get_project_settings
from youtube.spiders import YoutubeProfileSpider
import json

@defer.inlineCallbacks
def do_spider(runner, spider, spider_id, *args, **kwargs):
    yield runner.crawl(spider, spider_id=spider_id, *args, **kwargs)
    reactor.stop()

def switch_spider(name):
    switcher = {
        "youtube_profile_spider": YoutubeProfileSpider,
        # "youtube_channel_video": crawl_youtube_channel_video,
        # "youtube_channel_subscriber": crawl_youtube_channel_subscriber,
    }
    return switcher.get(name, "invalid spider")

def main():
    crawler_name = sys.argv[1]
    id = sys.argv[2]
    crawler_args = json.loads(sys.argv[3])
    spider = switch_spider(crawler_name)

    if spider == "invalid crawler":
        raise Exception("Invalid crawler \"{}\"".format(crawler_name))
        return
    
    runner = CrawlerRunner(get_project_settings())
    
    do_spider(runner, spider, id, **crawler_args)
    reactor.run()

if __name__ == "__main__":
    main()
