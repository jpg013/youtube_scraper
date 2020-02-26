def parse_subscriber_content_items(sel):
    return sel.xpath("//li[contains(@class, 'channels-content-item')]")

def parse_subscriber_load_more(sel):
    return sel.xpath("//button[contains(@class, 'load-more-button')]/@data-uix-load-more-href").get()