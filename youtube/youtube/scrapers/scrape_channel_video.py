def scrape_channel_video_duration(sel):
    results = { "duration": ""}
    video_time = sel.css('.video-time').xpath("./span/text()").get()

    if video_time is not None:
        results["duration"] = video_time

    return results

def scrape_channel_video_id(sel):
    results = { "id": ""}
    video_id = sel.css('.yt-lockup-video').attrib.get("data-context-item-id", None)

    if video_id is not None:
        results["id"] = video_id

    return results

def scrape_channel_video_links(sel):
    return sel.css("#channels-browse-content-grid").xpath('./li')

def scrape_channel_video_meta(sel):
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

def scrape_channel_video_thumbnail(sel):
    results = { "thumbnail": ""}

    video_thumbnail = sel.css('img').xpath("@src").get()

    if video_thumbnail is not None:
        results["thumbnail"] = video_thumbnail

    return results