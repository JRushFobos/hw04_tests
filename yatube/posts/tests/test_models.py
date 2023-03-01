from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_group_models_have_correct_object_names(self):
        '''Проверяем, что у моделей group корректно работает __str__ и
        Проверяем, что у моделей post корректно работает __str__.
        '''
        self.assertEqual(
            PostModelTest.group.title, str(PostModelTest.group.title)
        )
        self.assertEqual(
            PostModelTest.post.text[: Post.SYMBOL_POST_QUANTITY],
            str(PostModelTest.post),
        )

    def test_post_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_verboses = (
            ('text', 'Тест'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        )

        for value, expected in field_verboses:
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_post_help_text(self):
        '''help_text в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )
