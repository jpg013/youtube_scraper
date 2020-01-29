def parse_channel_about_stats(resp):
    results = {
        "view_count": 0,
        "joined_at": ""
    }

    stats_sel = resp.css(".about-stats")
    view_count = stats_sel.xpath("./span/b/text()").get()
    joined_at = stats_sel.xpath("./span[2]/text()").get()
    
    if view_count is not None:
        results["view_count"] = int(view_count.replace(",", ""))
    
    if joined_at is not None:
        results["joined_at"] = joined_at
    
    return results