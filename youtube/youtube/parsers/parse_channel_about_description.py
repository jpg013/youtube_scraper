def parse_channel_about_description(resp):
    results = {
        "description": ""
    }
    descr = resp.css(".about-description").xpath('./pre/text()').get()

    if descr is not None:
        results["description"] = descr

    return results