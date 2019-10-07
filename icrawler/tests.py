from django.core.cache import cache
from django.test import TestCase


class viewTests(TestCase):
    suffix = 'random_test_value'

    def test_get_posts_by_country(self):
        print("Test /get_posts_by_country no_such_value")
        response = self.client.get('/get_posts_by_country', {'country': self.suffix})
        self.assertEqual(response.content, "[]")


    def test_get_hype_by_tag(self):
        print("Test /test_get_hype_by_tag no_such_value")
        response = self.client.get('/get_hype_by_tag', {'hashtag': self.suffix})
        self.assertEqual(response.content, "[]")


    def test_get_dailypost_by_tag(self):
        print("Test /get_dailypost_by_tag no_such_value")
        response = self.client.get('/get_hype_by_tag', {'hashtag': self.suffix})
        self.assertEqual(response.content, "[]")