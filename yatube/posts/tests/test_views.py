from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

from django.conf import settings

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Вызывается один раз перед запуском всех тестов класса.'''
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mokrushin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост №1',
            group=cls.group,
        )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        index_context = {
            response.context['post'].text: self.post.text,
            response.context['post'].group: self.post.group,
            response.context['post'].author: self.post.author,
        }
        for value, expected in index_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_new_post_correct_context(self):
        '''Форма добавления поста с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)


class Paginator(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Вызывается один раз перед запуском всех тестов класса.'''
        super().setUpClass()
        cls.TOTAL_POSTS_COUNT = 13
        cls.NUMBER_LAST_PAGE = (
            cls.TOTAL_POSTS_COUNT // settings.NUM_POSTS
        ) + 1
        cls.POSTS_ON_LAST_PAGE = cls.TOTAL_POSTS_COUNT % settings.NUM_POSTS
        cls.user = User.objects.create_user(username='Mokrushin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        Post.objects.bulk_create(
            [
                Post(
                    author=cls.user,
                    text='Пост для пайджинга',
                    group=cls.group,
                )
                for post in range(cls.TOTAL_POSTS_COUNT)
            ]
        )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        '''Проверка: количество постов на первой странице равно 10'''
        addresses = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', args=[self.user.username]),
        )
        for address in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                count_post = len(response.context.get('page_obj'))
                self.assertEqual(count_post, settings.NUM_POSTS)

    def test_second_page_contains_three_records(self):
        '''Проверка: на второй странице должно быть три поста.'''
        addresses = (
            reverse('posts:index') + f'?page={self.NUMBER_LAST_PAGE}',
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + f'?page={self.NUMBER_LAST_PAGE}',
            reverse('posts:profile', args=[self.user.username])
            + f'?page={self.NUMBER_LAST_PAGE}',
        )

        for address in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                count_post = len(response.context.get('page_obj'))
                self.assertEqual(count_post, self.POSTS_ON_LAST_PAGE)
