def parse_channel_about_location(resp):
    results = {
        "location": ""
    }
    location = resp.css(".country-inline::text").get()
    
    if location is not None:
        results["location"] = location.strip()

    return results