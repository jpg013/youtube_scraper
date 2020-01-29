import urllib.parse

def parse_channel_about_links(resp):
    results = {
        "links": {}
    }

    secondary_links_sel = resp.css(".about-secondary-links").xpath("./li")
    custom_links_sel = resp.css(".about-custom-links").xpath("./li")

    def parse_link(sel):
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
        parse_link(li_sel)

    for li_sel in custom_links_sel:
        parse_link(li_sel)
    
    return results