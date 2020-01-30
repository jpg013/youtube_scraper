import sys
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
import logging
import youtube.spiders as spiders

@defer.inlineCallbacks
def youtube_channel_about_crawler(runner):
    yield runner.crawl(spiders.ChannelAboutSpider, channel_ids=[sys.argv[2]])
    reactor.stop()

@defer.inlineCallbacks
def youtube_channel_videos_crawler(runner):
    print("here!")
    yield runner.crawl(spiders.ChannelVideosSpider, channel_id=sys.argv[2])
    reactor.stop()


def switch_crawler(name):
    switcher = {
        "crawl_channel_about": youtube_channel_about_crawler,
        "crawl_channel_videos": youtube_channel_videos_crawler,
    }

    return switcher.get(name, "invalid crawler")

def main():
    crawl_func = switch_crawler(sys.argv[1])

    if crawl_func == "invalid crawler":
        print("invalid crawler")
        return
    
    runner = CrawlerRunner()
    crawl_func(runner)
    reactor.run()

if __name__ == "__main__":
    main()