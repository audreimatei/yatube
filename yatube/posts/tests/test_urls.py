from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            creator=cls.user_author,
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user_not_author)
        self.auth = Client()
        self.auth.force_login(PostsURLTests.user_author)

    def test_urls_exists_at_desired_location(self):
        responses = (
            self.client.get('/'),
            self.client.get(f'/group/{PostsURLTests.group.slug}/'),
            self.client.get(f'/profile/{PostsURLTests.user_author.username}/'),
            self.client.get(f'/posts/{PostsURLTests.post.id}/'),
            self.authorized_client.get('/create/'),
            self.auth.get(f'/posts/{PostsURLTests.post.id}/edit/'),
            self.authorized_client.get(
                f'/posts/{PostsURLTests.post.id}/comment/',
                follow=True
            ),
            self.authorized_client.get('/follow/'),
            self.authorized_client.get(
                f'/profile/{PostsURLTests.user_author.username}/follow/',
                follow=True
            ),
            self.authorized_client.get(
                f'/profile/{PostsURLTests.user_author.username}/unfollow/',
                follow=True
            ),
        )
        for response in responses:
            with self.subTest(url=response.request['PATH_INFO']):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_requierd_urls_redirect_anonymous_on_auth_login(self):
        urls = (
            '/create/',
            f'/posts/{PostsURLTests.post.id}/edit/',
            f'/posts/{PostsURLTests.post.id}/comment/',
            '/follow/',
            f'/profile/{PostsURLTests.user_author.username}/follow/',
            f'/profile/{PostsURLTests.user_author.username}/unfollow/',
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url, follow=True),
                    f'/auth/login/?next={url}'
                )

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{PostsURLTests.post.id}/')

    def test_unexisting_page_url_not_found(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        cache.clear()
        url_template_names = {
            '/': 'posts/index.html',
            f'/group/{PostsURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostsURLTests.user_author.username}/':
            'posts/profile.html',
            f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{PostsURLTests.post.id}/edit/': 'posts/post_create.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in url_template_names.items():
            with self.subTest(url=url):
                response = self.auth.get(url)
                self.assertTemplateUsed(response, template)
