import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            creator=cls.user,
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.yet_another_group = Group.objects.create(
            creator=cls.user,
            title='Другая тестовая группа',
            slug='yet-another-test-slug',
            description='Другое тестовое описание'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x37\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.another_uploaded = SimpleUploadedFile(
            name='another.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.yet_another_uploaded = SimpleUploadedFile(
            name='yet_another.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(PostsFormTests.user)

    def check_fields(self, post, form_data):
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(
            post.group,
            Group.objects.get(id=form_data['group'])
        )
        self.assertEqual(
            post.image.name.split('/')[1],
            form_data['image'].name
        )

    def test_post_create(self):
        form_data = {
            'text': 'Новый тестовый пост',
            'group': PostsFormTests.group.id,
            'image': PostsFormTests.another_uploaded
        }
        posts_ids = set(Post.objects.values_list('id', flat=True))
        self.auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_created = Post.objects.exclude(id__in=posts_ids).get()
        self.check_fields(post_created, form_data)

    def test_post_edit(self):
        form_data = {
            'text': 'Изменённый пост',
            'group': PostsFormTests.yet_another_group.id,
            'image': PostsFormTests.yet_another_uploaded
        }
        self.auth.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        post_edited = Post.objects.get(id=PostsFormTests.post.id)
        self.check_fields(post_edited, form_data)

    def test_add_comment(self):
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.auth.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostsFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        comments = response.context['comments']
        self.assertEqual(comments[0].text, form_data['text'])
