from django.contrib.auth import get_user_model
from django.test import TestCase

from yatube.settings import CHARS_SHOWN

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            creator=cls.user,
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        object_names = {
            str(PostModelTest.post): PostModelTest.post.text[:CHARS_SHOWN],
            str(PostModelTest.group): PostModelTest.group.title
        }
        for act, expected in object_names.items():
            with self.subTest(act=act):
                self.assertEqual(act, expected)
