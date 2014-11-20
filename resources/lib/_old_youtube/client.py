import json
import urlparse

import requests


__author__ = 'bromix'


class Client(object):
    BROWSE_ID_WHAT_TO_WATCH = 'FEwhat_to_watch'

    KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'  # TV

    def __init__(self, key='', language='en-US', items_per_page=50):
        self._key = self.KEY
        if key:
            self._key = key
            pass

        self._language = language
        self._country = language.split('-')[1]
        self._max_results = items_per_page
        pass

    def get_language(self):
        return self._language

    def get_channel_sections_v3(self, channel_id):
        """
        Returns the sections of a channel
        :param channel_id:
        :return:
        """
        params = {'part': 'snippet,contentDetails,id',
                  'channelId': channel_id}
        return self._perform_v3_request(method='GET', path='channelSections', params=params)

    def get_guide_v3(self):
        params = {'part': 'snippet',
                  'regionCode': self._country,
                  'hl': self._language}
        return self._perform_v3_request(method='GET', path='guideCategories', params=params)

    def get_what_to_watch_tv(self):
        return self.browse_id_tv(self.BROWSE_ID_WHAT_TO_WATCH)

    def browse_id_tv(self, browse_id):
        post_data = {'browseId': browse_id}
        return self._perform_tv_request(method='POST', path='browse', post_data=post_data)

    def get_guide_tv(self):
        return self._perform_tv_request(method='POST', path='guide')

    pass