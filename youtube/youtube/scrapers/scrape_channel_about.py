import urllib.parse

def scrape_channel_about_description(sel):
    results = {
        "description": ""
    }
    descr = sel.css(".about-description").xpath('./pre/text()').get()

    if descr is not None:
        results["description"] = descr

    return results

def scrape_channel_about_banner(sel):
    results = { "banner_url": "" }

    banner_sel = sel.css("#gh-banner").xpath("./style")

    if banner_sel is None:
        return results

    s = banner_sel.get()
    """
    The banner style element contains multiple media elements for different screen sizes.
    I am just pulling the first one (default) for now but we may want to grab the other sizes
    at some point.
    <style>
      #c4-header-bg-container {
            background-image: url(//yt3.ggpht.com/7tb798fXB5s28HBfg0hef6l2V4DZHAGyI2Micm9R6nL-Lp6Dayc1qzg_U59Sk8N0J4j9zWtWBg=w1060-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj);
        }
    </style>
    """
    results["banner_url"] = s[s.find("(")+1:s.find(")")]
    return results
    
    
def scrape_channel_about_links(sel):
    results = {
        "links": {}
    }

    secondary_links_sel = sel.css(".about-secondary-links").xpath("./li")
    custom_links_sel = sel.css(".about-custom-links").xpath("./li")

    def scrape_link(sel):
        source = sel.xpath('./a/@title').get()
        href = sel.xpath("./a/@href").get()
        if source is None or href is None:
            return
        key = source.lower()
        if key in results["links"].keys():
            return
        query_parts = urllib.parse.parse_qs(href)
        q = query_parts.get("/redirect?q", None) or query_parts.get("q", None)
        if q is not None:
            results["links"][key] = q[0]
    
    for li_sel in secondary_links_sel:
        scrape_link(li_sel)

    for li_sel in custom_links_sel:
        scrape_link(li_sel)
    
    return results

def scrape_channel_about_location(sel):
    results = {
        "location": ""
    }
    location = sel.css(".country-inline::text").get()
    
    if location is not None:
        results["location"] = location.strip()

    return results

def scrape_channel_about_name(sel):
    results = {
        "screen_name": "",
        "profile_image": "",
        "user_name": ""
    }
    
    profile_sel = sel.css(".channel-header-profile-image-container")

    if profile_sel is None:
        return results

    results["user_name"] = profile_sel.xpath("@href").get()

    profile_img_sel = sel.css('.channel-header-profile-image-container > img')

    if profile_img_sel is not None:
        attrs = profile_img_sel.attrib
        results["screen_name"] = attrs["title"]
        results["profile_image"] = attrs["src"]

    return results

def scrape_channel_about_stats(sel):
    results = {
        "view_count": 0,
        "joined_at": ""
    }

    stats_sel = sel.css(".about-stats")
    view_count = stats_sel.xpath("./span/b/text()").get()
    joined_at = stats_sel.xpath("./span[2]/text()").get()
    
    if view_count is not None:
        results["view_count"] = int(view_count.replace(",", ""))
    
    if joined_at is not None:
        results["joined_at"] = joined_at
    
    return results

def scrape_channel_about_subscriber_count(sel):
    results = { "subscriber_count": "" }

    sub_count = sel.css('.yt-subscription-button-subscriber-count-branded-horizontal::text').get()

    if results is not None:
        results["subscriber_count"] = sub_count
    
    return results

def scrape_channel_about_is_verified(sel):
    results = { "is_verified": False }
    is_verified = sel.css(".qualified-channel-title.has-badge").get() is not None
    results["is_verified"] = is_verified

    return results
    

