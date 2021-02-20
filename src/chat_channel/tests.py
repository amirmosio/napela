from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
# Create your tests here.
from django.urls import reverse

from chat_channel.models import ChatContact, ChatMessage


def create_user(username="test_username"):
    return User.objects.create_user(username, password="123456")


class AdScoreTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.u1 = create_user("u1")
        cls.u2 = create_user("u2")

    def test_loading_chat_page_and_create_contact(self):
        login = self.client.login(username='u1', password='123456')
        response = self.client.get(reverse('chat_channel:chat_page_with_contact', args=[self.u2.id]),
                                   {'addresser_username': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatContact.objects.filter(owner=self.u1, contact_user=self.u2).count(), 1)
        self.assertEqual(ChatContact.objects.filter(owner=self.u2, contact_user=self.u1).count(), 1)

    def get_prev_messages(self):
        login = self.client.login(username='u1', password='123456')
        response = self.client.get(reverse('chat_channel:chat_page_with_contact', args=[self.u2.id]),
                                   {'addresser_username': 'user'})

        c1 = ChatMessage.objects.create(owner=self.u1, to=self.u2, text="hello",
                                        created_datetime=datetime.now())
        c1 = ChatMessage.objects.create(owner=self.u1, to=self.u2, text="do you remember me?",
                                        created_datetime=datetime.now())
        c1 = ChatMessage.objects.create(owner=self.u2, to=self.u1, text="hi, amir :0", created_datetime=datetime.now())

        contact = ChatContact.objects.filter(owner=self.u1, contact_user=self.u2)
        response = self.client.get(reverse('chat_channel:get_pre_messages', args=[contact.id]), {})
        self.assertEqual(len(response['prev_messages']), 3)
