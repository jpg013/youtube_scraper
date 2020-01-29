def parse_channel_about_name(resp):
    profile_img_tag = resp.css('.channel-header-profile-image-container > img')
    results = {
        "name": "",
        "profile_image": "",
    }

    if profile_img_tag is not None:
        attrs = profile_img_tag.attrib
        results["name"] = attrs["title"]
        results["profile_image"] = attrs["src"]
    
    return results

