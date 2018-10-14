from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from .models import Post
from django.contrib.auth.models import User


class PostTestCase(LiveServerTestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'teste123'
        self.user = User.objects.create(username=self.username,
                                        password=self.password)

    def test_publish_post(self):
        post = Post(author=self.user, title='test',
                    text='hello, this is a test post')
        post.save()
        post.publish()
        self.assertTrue(post.published_date != None)

    def test_post_list(self):
        post = Post(author=self.user,
                    title='My title for my test post_list',
                    text='test')
        post.save()
        url = reverse('post_list')
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)
        self.assertFalse(post.title in str(response.content))
        post.publish()
        response = self.client.get(url)
        self.assertTrue(post.title in str(response.content))

    def test_post_detail_not_found(self):
        url = reverse('post_detail', kwargs={'pk': '1234'})
        response = self.client.get(url)
        self.assertTrue(response.status_code == 404)

    def test_post_detail_draft_not_logged_in(self):
        post = Post(author=self.user,
                    title='My title for draft not logged in test',
                    text='test text')
        post.save()
        url = reverse('post_detail', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertTrue(response.status_code == 404)

    def test_post_detail_draft_logged_in(self):
        post = Post(author=self.user,
                    title='My title for draft in logged in test',
                    text='test text')
        post.save()
        login = self.client.force_login(self.user)
        url = reverse('post_detail', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(post.title in str(response.content))
