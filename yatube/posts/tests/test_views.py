from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Вызывается один раз перед запуском всех тестов класса.'''
        super().setUpClass()
        cls.POSTS_ON_FIRST_PAGE = 10
        cls.POSTS_ON_SECOND_PAGE = 3
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

        # Создаем 13 постов
        for i in range(1, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Пост для пайджинга',
                group=cls.group,
            )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        # Собираем в словарь пары 'имя_html_шаблона: reverse(name)'
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args={self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', args={self.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы /index + пагинотор
    def test_index_page_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        index_context = {
            first_post.text: self.post.text,
            first_post.group: self.post.group,
            first_post.author: self.post.author,
        }
        for value, expected in index_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы /group_list + пагинотор
    def test_group_list_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_group = response.context['page_obj'][0]
        index_context = {
            first_group.text: self.post.text,
            first_group.group: self.post.group,
            first_group.author: self.post.author,
        }
        for value, expected in index_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы /profile + пагинотор
    def test_profile_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                args={self.user.username},
            )
        )
        first_group = response.context['page_obj'][0]
        index_context = {
            first_group.text: self.post.text,
            first_group.group: self.post.group,
            first_group.author: self.post.author,
        }
        for value, expected in index_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы /post_detail
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

    # Проверяем, что словарь context страницы /create_post(редактирование)
    def test_new_post_correct_context(self):
        '''Форма добавления поста с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    # Проверяем, что словарь context страницы /create_edit(редактирование)
    def test_context_in_post_edit(self):
        '''Форма редактирования поста с правильным контекстом'''
        url = reverse('posts:profile', args=[self.post.author.username])
        response = self.authorized_client.get(url)
        post = response.context['page_obj'][0]
        post_text_0 = post.text
        post_author_0 = self.post.author.username
        self.assertEqual(post_author_0, 'Mokrushin')
        self.assertEqual(post_text_0, 'Пост для пайджинга')

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_FIRST_PAGE
        )
        # Проверка: на второй странице должно быть три поста.

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_SECOND_PAGE
        )

    def test_first_page_group_list_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_FIRST_PAGE
        )

    def test_second_page_group_list_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_SECOND_PAGE
        )

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', args={self.user.username})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_FIRST_PAGE
        )

    def test_second_page_profile_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse('posts:profile', args={self.user.username}) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), self.POSTS_ON_SECOND_PAGE
        )

    def test_index_page_show_correct_context(self):
        '''Пост отображается на главной странице'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Пост для пайджинга')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_group_page_show_correct_context(self):
        '''Пост отображается на странице группы'''
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title

        self.assertEqual(post_text_0, 'Пост для пайджинга')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_profile_page_show_correct_context(self):
        '''Пост отображается на странице группы'''
        response = self.authorized_client.get(
            reverse('posts:profile', args={self.user})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title

        self.assertEqual(post_text_0, 'Пост для пайджинга')
        self.assertEqual(post_group_0, 'Тестовая группа')
