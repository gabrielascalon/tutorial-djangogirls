from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from .models import Post, Comment
from django.contrib.auth.models import User


class PostTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'teste123'
        self.user = User.objects.create(username=self.username,
                                        password=self.password)

    def test_publish_post(self):
        post = Post(author=self.user, title='My title for publish post test',
                    text='Hello, this is a test post')
        post.save()
        url = reverse('post_list')
        response = self.client.get(url)
        self.assertTrue(post.title not in str(response.content))
        post.publish()
        self.assertTrue(post.published_date != None)


    def test_post_list(self):
        post = Post(author=self.user,
                    title='My title for my test post_list',
                    text='Hello, this is a test post')
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
        self.client.force_login(self.user)
        url = reverse('post_detail', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(post.title in str(response.content))

    def test_publish_new_post(self):
        data = {'title':'This is as test title for publishing',
                'text':'Hello, this is a post for publish test'}
        self.client.force_login(self.user)
        response = self.client.post(reverse('post_new'), data, follow=True)
        self.assertTrue(data['title'] in str(response.content))

    def test_edit_post_not_logged_in(self):
        post = Post(author=self.user,
             title='This is the title for the edit while not logged in test',
             text='This is a text for the not logged in edit test')
        post.save()
        post.publish()
        url = reverse('post_edit', kwargs={'pk': post.pk})
        response = self.client.post(url, follow=True)
        self.assertFalse(post.title in str(response.content))
        self.assertTrue(response.template_name == ['registration/login.html'])

    def test_edit_post_logged_in(self):
        post = Post(author=self.user,
                    title='This is the title for the edit while logged in test',
                    text='This is a text for the logged in edit test')
        post.save()
        post.publish()
        self.client.force_login(self.user)
        edited_post = {'title': 'This is the edited title',
                       'text':'This is the edited text'}
        url = reverse('post_edit', kwargs={'pk': post.pk})
        response = self.client.post(url, edited_post,
                                    kwargs={'pk':post.pk}, follow=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(edited_post['title'] in str(response.content))

    def test_delete_post(self):
        post = Post(author=self.user,
                    title='This is the title for the deleting a post test',
                    text='This is the text for the deleting a post test')
        post.save()
        post.publish()
        url = reverse('post_list')
        response = self.client.get(url)
        self.assertTrue(post.title in str(response.content))
        post.delete()
        response = self.client.get(url)
        self.assertFalse(post.title in str(response.content))

class CommentTestCase(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'teste123'
        self.user = User.objects.create(username=self.username,
                                        password=self.password)
        self.title = 'This is a comment test post'
        self.text = 'This is a test post text'
        self.post = Post.objects.create(author=self.user,
                                        title=self.title,
                                        text=self.text)
        self.post.publish()


    def test_create_comment(self):
        comment = Comment(post=self.post,
                          author='Test author general comment',
                          text='This is a comment')
        comment.save()
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertFalse(comment.author in str(response.content))
        comment.approve()
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertTrue(comment.author in str(response.content))

    def test_not_evaluated_comment_logged_in_user(self):
        comment = Comment(post=self.post,
                          author='Test author not evaluated',
                          text='This is a not evaluated comment')
        comment.save()
        self.client.force_login(self.user)
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertTrue((comment.author in str(response.content)))

    def test_rejected_comment(self):
        comment = Comment(post=self.post,
                          author='Test author rejected',
                          text='This is a rejected comment')
        comment.save()
        self.client.force_login(self.user)
        url = reverse('post_detail', kwargs={'pk' : self.post.pk})
        response = self.client.get(url)
        self.assertTrue(comment.author in str(response.content))
        comment.delete()
        response = self.client.get(url)
        self.assertFalse(comment.author in str(response.content))
