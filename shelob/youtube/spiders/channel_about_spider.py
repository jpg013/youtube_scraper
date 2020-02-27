import scrapy
from scrapy import signals
from scrapy.loader import ItemLoader
from .base_youtube_spider import BaseYoutubeSpider
import youtube.parsers.parse_channel_about as parsers
from youtube.items import ChannelAboutItem, ChannelLinkItem
import dpath.util
import json

def _finditem(obj, key):
    if obj is None:
        return

    if not isinstance(obj, dict) and not isinstance(obj, list):
        return
    
    if key in obj: return obj[key]
    if isinstance(obj, dict):
        for k, v in obj.items():    
            item = _finditem(v, key)
            if item is not None:
                return item
    elif isinstance(obj, list):
        for v in obj:
            item = _finditem(v, key)
            if item is not None:
                return item

def parse_location(obj):
    root = _finditem(obj, "country")
    if root is None:
        return
    return root.get("simpleText", None)

def parse_description(obj):
    root = _finditem(obj, "channelAboutFullMetadataRenderer")
    if root is None:
        return
    return root.get("description", {}).get("simpleText", None)

def parse_channel_id(obj):
    root = _finditem(obj, "channelAboutFullMetadataRenderer")
    if root is None:
        return
    return root.get("channelId", None)

def parse_joined_date_text(obj):
    root = _finditem(obj, "joinedDateText")
    if root is None:
        return
    run = root.get("runs", [])[1]
    if run is None:
        return
    return run.get("text", None)    

def parse_banner_url(obj):
    header = obj.get("header")
    if header is None:
        return
    banner = _finditem(header, "banner")
    if banner is None:
        return
    thumbnail = banner.get("thumbnails", [])[0]
    if thumbnail is None:
        return
    return thumbnail.get("url", None)

def parse_view_count(obj):
    text = _finditem(obj, "viewCountText")
    if text is None:
        return
    run = text.get("runs", [])[0]
    if run is None:
        return
    return run.get("text", None)    

def parse_avatar_url(obj):
    meta = _finditem(obj, "channelAboutFullMetadataRenderer")
    if meta is None:
        return
    return dpath.util.get(meta, "/avatar/thumbnails/0/url")

def parse_primary_links(obj):
    try:
        meta = _finditem(obj, "channelAboutFullMetadataRenderer")
        if meta is None:
            return []
        def link_mapper(item):
            return {
                "source": dpath.util.get(item, "/title/simpleText"),
                "url": dpath.util.get(item, "/navigationEndpoint/urlEndpoint/url")
            }
        return list(map(link_mapper, dpath.util.get(meta, "/primaryLinks")))
    except Exception:
        return []

def parse_subscriber_count_text(obj):
    item = dpath.util.get(obj, "/header/c4TabbedHeaderRenderer/subscriberCountText/runs")[0]
    if item is None:
        return
    return item.get("text", None)

def parse_is_verified(obj):
    try:
        badges = dpath.util.get(obj, "/header/c4TabbedHeaderRenderer/badges")
        if badges is None:
            return False
        for badge in badges:
            style = dpath.util.get(badge, "/metadataBadgeRenderer/style")
            if style == "BADGE_STYLE_TYPE_VERIFIED":
                return True
        return False
    except Exception:
        return False

    return False

def parse_screen_name(obj):
    return dpath.util.get(obj, "/header/c4TabbedHeaderRenderer/title")

def parse_user_name(obj):
    return dpath.util.get(obj, "/header/c4TabbedHeaderRenderer/navigationEndpoint/commandMetadata/webCommandMetadata/url")

    
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
        
        yield scrapy.Request(
            url=url, 
            callback=self.handle_response,
            errback=self.handle_error
        )

    def parse_data(self, json_data):
        # l = ItemLoader(item=AboutChannelItem(), response=response)
        # l.add_css("location", ".country-inline::text")
        # l.add_xpath("description", "//div[contains(@class,'about-description')]/pre/text()")
        # l.add_xpath("banner_url", "//div[contains(@id,'gh-banner')]/style/text()")
        # l.add_css("subscriber_count", ".yt-subscription-button-subscriber-count-branded-horizontal::text")
        # l.add_css("is_verified", ".qualified-channel-title.has-badge")
        # l.add_xpath("joined_at", "//div[contains(@class, 'about-stats')]/span[2]/text()")
        # l.add_xpath("view_count", "//div[contains(@class, 'about-stats')]/span/b/text()")
        # l.add_xpath("user_name", "//a[contains(@class, 'channel-header-profile-image-container')]/@href")
        # l.add_xpath("screen_name", "//a[contains(@class, 'channel-header-profile-image-container')]/img/@title")
        # l.add_xpath("profile_image", "//a[contains(@class, 'channel-header-profile-image-container')]/img/@src")
        # for link in parsers.parse_channel_about_links(response):
        #     l.add_value("links", link)
        l = ItemLoader(item=ChannelAboutItem())
        l.add_value("location", parse_location(json_data))
        l.add_value("description", parse_description(json_data))
        l.add_value("banner_url", parse_banner_url(json_data))
        l.add_value("subscriber_count", parse_subscriber_count_text(json_data))
        l.add_value("is_verified", parse_is_verified(json_data))
        l.add_value("joined_at", parse_joined_date_text(json_data))
        l.add_value("view_count", parse_view_count(json_data))
        l.add_value("user_name", parse_user_name(json_data))
        l.add_value("screen_name", parse_screen_name(json_data))
        l.add_value("profile_image", parse_avatar_url(json_data))
        
        primary_links = parse_primary_links(json_data) or []

        def map_link(item):
            link_loader = ItemLoader(item=ChannelLinkItem())
            link_loader.add_value("source", item["source"])
            link_loader.add_value("url", item["url"])
            return link_loader.load_item()
        
        l.add_value("links", list(map(map_link, primary_links)))
        return l.load_item()

    def extract_initial_data_json(self, text):
        start_ref = "window[\"ytInitialData\"] ="
        end_ref = "};" 
        
        try:
            start_idx = text.index(start_ref)
            sub_str = text[start_idx + len(start_ref):]
            end_idx = sub_str.index(end_ref)

            return sub_str[0:end_idx+len(end_ref)-1]
        except Exception as e:
            print("Cannot extract initial data json: ", e)

    def handle_response(self, response):
        try:        
            self.store_response(response, self.spider_id, ChannelAboutSpider.name)
            
            initial_data_json = self.extract_initial_data_json(response.text)
            if initial_data_json is None:
                print("What the fuck we dont have data.")
                return

            self.spider_results = self.parse_data(json.loads(initial_data_json))
        except Exception as e:
            print(e)

    def handle_error(self, failure):
        print("in the handle error")
        print(failure)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ChannelAboutSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        print("SPIDER IS GETTING CLOSED", reason)

        try:
            results = dict(self.spider_results)
            results["links"] = list(map(lambda x: dict(x), results["links"]))
            self.store_spider_results(results)
        except Exception as e:
            print(e)
