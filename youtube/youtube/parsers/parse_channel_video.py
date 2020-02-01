import json
from scrapy.selector import Selector

def parse_channel_video_links(sel):
    """Parses channel video links for initial request"""
    return sel.css("#channels-browse-content-grid").xpath('./li')

def parse_channel_video_continuation_links(resp):
    """Parses channel video links for continuation response"""
    jsonresponse = json.loads(resp.body_as_unicode())
    sel = Selector(text=jsonresponse.get("content_html"))
    return sel.xpath("//li[contains(@class,'channels-content-item')]")

def parse_continuation_url(resp):
    """Parses url for continuation response"""
    jsonresponse = json.loads(resp.body_as_unicode())
    sel = Selector(text=jsonresponse.get("load_more_widget_html"))
    return parse_next_url(sel)

def parse_next_url(sel):
    """Parses the next request url from the response"""
    more_sel = sel.css(".load-more-button")

    if more_sel is None:
        return

    return more_sel.attrib.get("data-uix-load-more-href", None)

