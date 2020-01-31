import scrapy
import re
from scrapy.loader.processors import MapCompose, TakeFirst
import urllib.parse

def strip(value):
    """strip removes all whitespace around string"""
    return value.strip() if isinstance(value, str) else ""

def lower(value):
    """lower converts string to lowercase"""
    return value.lower() if isinstance(value, str) else ""

def extract_within_paren(value):
    """Pulls all character within first instance of open / close parens"""
    if not isinstance(value, str):
        return ""

    return value[value.find("(")+1:value.find(")")]

def exists(value):
    """Returns True if value exists else false"""
    return True if value is not None else False;

def with_replace(old, new=""):
    return lambda x: x.replace(old, new) if isinstance(x, str) else ""

def extract_link_href(value):
    if value is None:
        return ""
    
    query_parts = urllib.parse.parse_qs(value)
    return query_parts.get("/redirect?q", None) or query_parts.get("q", None)

def extract_digits(value):
    if not isinstance(value, str):
        return
    
    digits = re.findall(r'\d+', value)
    
    return "".join(digits)

class ChannelVideoItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    view_count = scrapy.Field(
        input_processor=MapCompose(strip, extract_digits),
        output_processor=TakeFirst()
    )
    duration = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    thumbnail = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    created_at = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )    

class ChannelLinkItem(scrapy.Item):
    source = scrapy.Field(
        input_processor=MapCompose(strip, lower),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        input_processor=MapCompose(strip, extract_link_href),
        output_processor=TakeFirst(),
    )

class AboutChannelItem(scrapy.Item):
    screen_name = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    user_name = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    profile_image = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    banner_url = scrapy.Field(
        input_processor=MapCompose(strip, extract_within_paren),
        output_processor=TakeFirst()
    )
    subscriber_count = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    is_verified = scrapy.Field(
        input_processor=MapCompose(exists),
        output_processor=TakeFirst()
    )
    joined_at = scrapy.Field(
        input_processor=MapCompose(lower, with_replace("joined"), strip),
        output_processor=TakeFirst()
    )
    view_count = scrapy.Field(
        input_processor=MapCompose(with_replace(","), strip),
        output_processor=TakeFirst()
    )
    links = scrapy.Field()
