import urllib.parse
from scrapy.loader import ItemLoader
from youtube.items import YoutubeLinkItem

def parse_channel_profile_links(response):
    links = []
    links_sel = response.xpath("//li[@class='channel-links-item']")
    
    if links_sel is None:
        return []

    def parse_link(sel):
        try:
            loader = ItemLoader(item=ChannelLinkItem(), selector=sel)
            loader.add_xpath("source", "./a/@title")
            loader.add_xpath("url", "./a/@href")
            return loader.load_item()

            return x
        except Exception as e:
            print(e)
    
    # link set for quick lookup
    link_set = set()
    
    for li_sel in links_sel:
        link = parse_link(li_sel)
        link_id = "{}_{}".format(link.get("source"), link.get("url"))
        if link_id not in link_set:
            link_set.add(link_id)
            links.append(link)

    return links
    


