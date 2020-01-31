def parse_channel_video_links(sel):
    return sel.css("#channels-browse-content-grid").xpath('./li')

def parse_channel_video_meta(sel):
    results = {
        "view_count": 0,
        "created_at": ""
    }
    video_meta_sel = sel.css('.yt-lockup-meta-info')

    if video_meta_sel is None:
        return results
    
    video_view_count = video_meta_sel.xpath("./li[1]/text()").get()
    video_created_at = video_meta_sel.xpath("./li[2]/text()").get()

    results["view_count"] = int(video_view_count.split()[0].replace(",", ""))
    results["created_at"] = video_created_at

    return results

def parse_next_url(sel):
    more_sel = sel.css(".load-more-button")

    if more_sel is None:
        return

    return more_sel.attrib.get("data-uix-load-more-href", None)

