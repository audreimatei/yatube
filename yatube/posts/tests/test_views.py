import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

from yatube.settings import POSTS_PER_PAGE

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user = User.objects.create_user(username='an_auth')
        cls.yet_another_user = User.objects.create_user(username='yet_an_auth')
        cls.group = Group.objects.create(
            creator=cls.user,
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for i in range(1, 13):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост №{i}',
                group=cls.group,
                image=uploaded
            )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Test comment',
            author=cls.user,
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth = Client()
        self.another_auth = Client()
        self.yet_another_auth = Client()
        self.auth.force_login(PostsViewTests.user)
        self.another_auth.force_login(PostsViewTests.another_user)
        self.yet_another_auth.force_login(PostsViewTests.yet_another_user)

    def check_post_fields(self, page):
        self.assertEqual(page.id, PostsViewTests.post.id)
        self.assertEqual(page.author, PostsViewTests.post.author)
        self.assertEqual(page.text, PostsViewTests.post.text)
        self.assertEqual(page.group, PostsViewTests.post.group)
        self.assertEqual(page.image, PostsViewTests.post.image)

    def test_pages_uses_correct_templates(self):
        cache.clear()
        page_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewTests.post.id}
            ): 'posts/post_create.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reversed_name, template in page_template_names.items():
            with self.subTest(reversed_name=reversed_name, template=template):
                response = self.auth.get(reversed_name)
                self.assertTemplateUsed(response, template)

    def test_first_pages_contains_ten_records(self):
        cache.clear()
        responses = (
            self.client.get(reverse('posts:index')),
            self.client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': PostsViewTests.group.slug}
                )
            ),
            self.client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': PostsViewTests.user.username}
                )
            ),
        )
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_pages_contains_three_records(self):
        cache.clear()
        responses = (
            self.client.get(reverse('posts:index') + '?page=2'),
            self.client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': PostsViewTests.group.slug}
                ) + '?page=2'
            ),
            self.client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': PostsViewTests.user.username}
                ) + '?page=2'
            )
        )
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']),
                    Post.objects.count() - POSTS_PER_PAGE
                )

    def test_home_page_show_correct_context(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.check_post_fields(response.context['page_obj'][0])

    def test_group_list_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewTests.group.slug}
            )
        )
        self.check_post_fields(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsViewTests.user.username}
            )
        )
        self.check_post_fields(response.context['page_obj'][0])

    def test_post_detail_page_show_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsViewTests.post.id}
            )
        )
        self.check_post_fields(response.context['post'])
        self.assertEqual(
            response.context['comments'][0],
            PostsViewTests.comment
        )

    def test_post_create_page_show_correct_context(self):
        response = self.auth.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.auth.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsViewTests.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_follow_index_page_only_following(self):
        Follow.objects.create(
            user=PostsViewTests.another_user,
            author=PostsViewTests.user
        )
        Follow.objects.create(
            user=PostsViewTests.another_user,
            author=PostsViewTests.yet_another_user
        )
        Follow.objects.create(
            user=PostsViewTests.yet_another_user,
            author=PostsViewTests.user
        )
        self.assertEqual(
            self.another_auth.get(
                reverse('posts:follow_index')).context['page_obj'][0],
            self.yet_another_auth.get(
                reverse('posts:follow_index')).context['page_obj'][0]
        )
        Post.objects.create(
            author=PostsViewTests.yet_another_user,
            text='New post'
        )
        self.assertNotEqual(
            self.another_auth.get(
                reverse('posts:follow_index')).context['page_obj'][0],
            self.yet_another_auth.get(
                reverse('posts:follow_index')).context['page_obj'][0]
        )

    def test_profile_follow_page(self):
        self.assertFalse(Follow.objects.filter(
            user=PostsViewTests.another_user,
            author=PostsViewTests.user).exists()
        )
        self.another_auth.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewTests.user.username}
            )
        )
        self.assertTrue(Follow.objects.filter(
            user=PostsViewTests.another_user,
            author=PostsViewTests.user).exists())

    def test_profile_unfollow_page(self):
        Follow.objects.create(
            user=PostsViewTests.another_user,
            author=PostsViewTests.user
        )
        self.another_auth.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostsViewTests.user.username}
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=PostsViewTests.another_user,
            author=PostsViewTests.user).exists())

    def test_cache(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        Post.objects.create(
            author=PostsViewTests.user,
            text='New post'
        )
        response_with_new_post = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_with_new_post.content)
        cache.clear()
        response_cleared_cache = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_cleared_cache)
