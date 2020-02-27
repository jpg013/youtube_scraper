import scrapy
import re
from scrapy.loader.processors import MapCompose, TakeFirst
import urllib.parse

def strip(value):
    """strip removes all whitespace around string"""
    return value.strip() if isinstance(value, str) else ""

def to_int(value):
    """tries to convert value to int"""
    try:
        return int(value)
    except:
        return value

def lower(value):
    """lower converts string to lowercase"""
    return value.lower() if isinstance(value, str) else ""

def remove_beginning_slashes(value):
    """Removes starting slashes // from urls"""
    if not isinstance(value, str):
        return ""
    
    if value.startswith("//"):
        return value[2:]
    return value

def extract_within_paren(value):
    """Pulls all character within first instance of open / close parens"""
    if not isinstance(value, str):
        return ""

    return value[value.find("(")+1:value.find(")")]

def exists(value):
    """Returns True if value exists else false"""
    return True if value is not None else False;

def to_boolean(value):
    """Returns True if value is True else False"""
    return True if value is True else False;

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

def extract_channel_id_from_path(value):
    if not isinstance(value, str):
        return
    
    return value.split("/")[-1]

def transform_subscriber_count(value):
    """takes a subscriber count display string in the format of 
    (127, 243K, 12.5M) and transforms it to integer value"""
    if not isinstance(value, str):
        return

    ch = value[-1].lower()
    digits = value[:-1]

    if ch == "k":
        zero_count = 3
        return digits.ljust(len(digits) + zero_count, "0")

    if ch == "m":
        parts = digits.split(".")
        pre_count = parts[0]
        post_count = parts[1]
        zero_count = 6 - (len(post_count))
        return digits.replace(".", "").ljust(len(post_count + pre_count) + zero_count, "0")

    return value

class ChannelSubscriberItem(scrapy.Item):
    channel_id = scrapy.Field(
        input_processor=MapCompose(extract_channel_id_from_path),
        output_processor=TakeFirst(),
    )

    name = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst(),
    )

    subscriber_count = scrapy.Field(
        input_processor=MapCompose(strip, transform_subscriber_count, to_int),
        output_processor=TakeFirst(),
    )

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

class ChannelAboutItem(scrapy.Item):
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
        input_processor=MapCompose(strip, remove_beginning_slashes),
        output_processor=TakeFirst()
    )
    subscriber_count = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    is_verified = scrapy.Field(
        input_processor=MapCompose(to_boolean),
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
