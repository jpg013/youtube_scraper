import scrapy
import os
import datetime

BASE_YOUTUBE_URL="https://www.youtube.com"

"""BaseYoutubeSpider class is base spider to be inherited from by 
all youtube spiders. This class should never be instantiated
alone, only inherited from."""
class BaseYoutubeSpider(scrapy.Spider):
    name="base_youtube_spider"

    def __init__(self, *args, **kwargs):
        super(BaseYoutubeSpider, self).__init__(*args, **kwargs)

    def make_channel_about_url(self, channel_id):
        return f"{BASE_YOUTUBE_URL}/channel/{channel_id}/about"

    def make_channel_video_url(self, channel_id, sort):
        return f"{BASE_YOUTUBE_URL}/channel/{channel_id}/videos?view=0&sort=dd&flow=grid"

    def closed(reason):
        print("handling the close")
        print(reason)

    def store_response(self, resp):
        url_parts = resp.url.split(BASE_YOUTUBE_URL)

        if len(url_parts) != 2:
            return

        now = datetime.datetime.now().replace(microsecond=0).isoformat()
        filename = "{}{}.html".format(now, url_parts[1].replace("/", "_"))

        path = os.path.join('tmp', "youtube", filename)

        with open(path, 'wb') as f:
            f.write(resp.body)
        
        self.log('saved response %s' % filename)



