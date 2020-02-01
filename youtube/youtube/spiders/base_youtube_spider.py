import scrapy
import os
import json

"""BaseYoutubeSpider class is base spider to be inherited from by 
all youtube spiders. This class should never be instantiated
alone, only inherited from."""
class BaseYoutubeSpider(scrapy.Spider):
    name="base_youtube_spider"

    base_url="https://www.youtube.com"

    def __init__(self, *args, **kwargs):
        super(BaseYoutubeSpider, self).__init__(*args, **kwargs)

    def make_channel_about_url(self, channel_id):
        return f"{BASE_YOUTUBE_URL}/channel/{channel_id}/about"

    def make_channel_video_url(self, channel_id, sort):
        return f"{BASE_YOUTUBE_URL}/channel/{channel_id}/videos?view=0&sort=dd&flow=grid"

    def get_base_url(self):
        return BaseYoutubeSpider.base_url

    def store_response(self, key, data):
        path = os.path.join('tmp', "youtube", "{}.json".format(key))
        print(path)
        with open(path, 'w', encoding="utf8") as outfile:
            json.dump(data, outfile)
        
        self.log('saved response %s' % path)



