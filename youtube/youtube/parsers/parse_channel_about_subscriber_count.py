def parse_channel_about_subscriber_count(resp):
    results = { "subscriber_count": "" }

    sub_count = resp.css('.yt-subscription-button-subscriber-count-branded-horizontal::text').get()

    if results is not None:
        results["subscriber_count"] = sub_count
    
    return results