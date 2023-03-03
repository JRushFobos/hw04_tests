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

    def test_show_correct_context_index_group_list_profile(self):
        '''Шаблон index group_list profile сформирован с правильным
        контекстом.
        '''
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        objects = (
            (response_index.context['page_obj'][0].text, self.post.text),
            (response_index.context['page_obj'][0].group, self.post.group),
            (response_index.context['page_obj'][0].author, self.post.author),
            (response_group_list.context['page_obj'][0].text, self.post.text),
            (
                response_group_list.context['page_obj'][0].group,
                self.post.group,
            ),
            (
                response_group_list.context['page_obj'][0].author,
                self.post.author,
            ),
            (response_profile.context['page_obj'][0].text, self.post.text),
            (response_profile.context['page_obj'][0].group, self.post.group),
            (response_profile.context['page_obj'][0].author, self.post.author),
        )
        for object, data in objects:
            with self.subTest(object=object):
                self.assertEqual(object, data)

    def test_show_correct_context_post_detail(self):
        '''Шаблон post_detail сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        context = (
            (
                response.context['post'].text,
                self.post.text,
            ),
            (
                response.context['post'].group,
                self.post.group,
            ),
            (
                response.context['post'].author,
                self.post.author,
            ),
        )
        for value, expected in context:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_show_correct_object_group_list(self):
        '''Проверка страницы группы передается объект группы.'''
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        objects = (
            (response.context.get('group').title, self.post.group.title),
            (response.context.get('group').slug, self.post.group.slug),
            (
                response.context.get('group').description,
                self.post.group.description,
            ),
        )
        for value, expected in objects:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_create_post_correct_context(self):
        '''Форма добавления поста с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_create_edit_correct_context(self):
        '''Шаблон create_edit сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_with_group_not_shown_on_page_another_group(self):
        '''Проверяем пост с группой не отображается в другой группе.'''
        form_fields = (
            (
                (
                    reverse(
                        'posts:group_list', kwargs={'slug': self.group.slug}
                    )
                ),
                (Post.objects.exclude(group=self.post.group)),
            ),
        )
        for value, expected in form_fields:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_check_post_in_another_pages(self):
        '''Проверяем пост отобржается на index, group_list,
        profile страницах.
        '''
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)


class Paginator(TestCase):
    TOTAL_POSTS_COUNT = 13
    NUMBER_LAST_PAGE = (TOTAL_POSTS_COUNT + 9) // settings.NUM_POSTS

    def posts_on_last_page(TOTAL_POSTS_COUNT):
        if TOTAL_POSTS_COUNT % settings.NUM_POSTS == 0:
            return settings.NUM_POSTS
        else:
            return TOTAL_POSTS_COUNT % settings.NUM_POSTS

    POSTS_ON_LAST_PAGE = posts_on_last_page(TOTAL_POSTS_COUNT)

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
