import os

from django.contrib.auth.models import User
from django.core.files.base import File
from django.test import TestCase
# Create your tests here.
from django.urls import reverse

from BookAdvertisement.models import BookAd
from user_score.models import AdScore


def create_book_ad(owner_username="test_username", title="test_title", author="test_author", description="test_desc",
                   sell=True,
                   poster_url=None, addresser_username=None, status="ACCEPTED"):
    book_ad = BookAd.objects.create(owner=User.objects.get(username=owner_username), title=title, author=author,
                                    description=description, sell=sell,
                                    addresser=User.objects.get(
                                        username=addresser_username) if addresser_username is not None else None,
                                    status=status)
    if poster_url:
        book_ad.poster.save(
            os.path.basename(poster_url),
            File(open(poster_url, 'rb'))
        )
        book_ad.save()
    return book_ad


def create_user(username="test_username"):
    return User.objects.create_user(username, password="123456")


class AdScoreTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        create_user("user")
        create_user("owner")
        cls.a1: BookAd = create_book_ad(owner_username="owner", addresser_username="user", status="DONE")
        cls.a2 = create_book_ad(owner_username="owner")

    def test_setting_addresser(self):
        login = self.client.login(username='owner', password='123456')
        response = self.client.post(reverse('user_score:set_addresser_and_done', args=[self.a2.id]), {'addresser_username': 'user'})
        self.assertEqual(response.status_code, 302)
        self.a2 = BookAd.objects.get(id=self.a2.id)
        self.assertEqual(self.a2.addresser.username, 'user')
        self.assertEqual(self.a2.status, 'DONE')

    def test_scoring(self):
        login = self.client.login(username='user', password='123456')
        response = self.client.post(reverse('user_score:give_score', args=[self.a1.id]), {'score': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AdScore.objects.filter(advertisement=self.a1).count(), 1)

    def test_editing_score(self):
        login = self.client.login(username='user', password='123456')
        response = self.client.post(reverse('user_score:give_score', args=[self.a1.id]), {'score': '1'})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('user_score:give_score', args=[self.a1.id]), {'score': '2'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AdScore.objects.filter(advertisement=self.a1).count(), 1)
        self.assertEqual(AdScore.objects.filter(advertisement=self.a1).last().score, 2)

    def test_owner_total_score(self):
        login = self.client.login(username='owner', password='123456')
        response = self.client.post(reverse('user_score:set_addresser_and_done', args=[self.a2.id]), {'addresser_username': 'user'})


        login = self.client.login(username='user', password='123456')
        self.client.post(reverse('user_score:give_score', args=[self.a1.id]), {'score': '1'})
        self.client.post(reverse('user_score:give_score', args=[self.a2.id]), {'score': '3'})
        self.assertEqual(self.a1.owner_score(), '2.0')

    def test_score_owner_and_addresser_matching(self):
        login = self.client.login(username='owner', password='123456')
        response = self.client.post(reverse('user_score:set_addresser_and_done', args=[self.a2.id]), {'addresser_username': 'user'})


        login = self.client.login(username='user', password='123456')
        self.client.post(reverse('user_score:give_score', args=[self.a1.id]), {'score': '1'})


        self.client.post(reverse('user_score:give_score', args=[self.a2.id]), {'score': '3'})
        self.assertEqual(self.a1.owner_score(), '2.0')
