from http import HTTPStatus
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
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
            text='Тестовый пост',
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

    def test_status_code_template_non_auth_and_auth(self):
        '''Тесты статусов ответов и шаблонов неавторизированного и
        авторизированного пользователя.
        '''
        templates_url_names = [
            ('/', HTTPStatus.OK, False),
            (
                f'/group/{self.group.slug}/',
                HTTPStatus.OK,
                False,
            ),
            (
                f'/profile/{self.user}/',
                HTTPStatus.OK,
                False,
            ),
            (f'/posts/{self.post.id}/', HTTPStatus.OK, False),
            ('/about/tech/', HTTPStatus.OK, False),
            ('/about/author/', HTTPStatus.OK, False),
            ('/auth/login/', HTTPStatus.OK, False),
            (f'/posts/{self.post.id}/edit/', HTTPStatus.FOUND, False),
            ('/create/', HTTPStatus.OK, True),
            ('/auth/password_change/', HTTPStatus.OK, True),
            ('/auth/password_reset/', HTTPStatus.OK, True),
            ('/auth/logout/', HTTPStatus.OK, True),
            ('/unexisting_page', HTTPStatus.NOT_FOUND, False),
        ]

        for address, code, auth in templates_url_names:
            with self.subTest(address=address):
                if auth:
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, code)
                elif not auth:
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, code)

    def test_status_code_template_non_aut(self):
        '''Тесты шаблонов неавторизированного
        пользователя.
        '''
        templates_url_names = [
            ('/', 'posts/index.html'),
            (
                f'/group/{self.group.slug}/',
                'posts/group_list.html',
            ),
            (f'/profile/{self.user}/', 'posts/profile.html'),
            (
                f'/posts/{self.post.id}/',
                'posts/post_detail.html',
            ),
            ('/about/tech/', 'about/tech.html'),
            ('/about/author/', 'about/author.html'),
            ('/auth/login/', 'users/login.html'),
        ]

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_correct_status_code_template_auth(self):
        '''Тесты статусов ответов авторизированного пользователя.'''
        templates_url_names = [
            (f'/posts/{self.post.id}/edit/', 'posts/create_post.html'),
            ('/create/', 'posts/create_post.html'),
            ('/auth/password_change/', 'users/password_change_form.html'),
            ('/auth/password_reset/', 'users/password_reset_form.html'),
            ('/auth/logout/', 'users/logged_out.html'),
        ]

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница /posts/<post_id>/edit/ доступна любому пользователю.'''
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/')
        )

    def test_about_tech_url_exists_at_desired_location(self):
        '''Страница / доступна любому пользователю.'''
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location(self):
        '''Страница /create/ доступна любому пользователю.'''
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_redirect_edit_post_url_unauthorized_user(self):
        '''Проверка редиректа анонимного пользователя со страницы
        редактирования поста
        '''
        response = self.guest_client.get(
            f'/posts/{PostUrlTest.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{PostUrlTest.post.pk}/edit/')
        )

    def test_name_address(self):
        '''Проверка соответствия фактических адресов страниц с их именами.'''
        templates_address_names = [
            ('/', reverse('posts:index')),
            (
                f'/group/{self.group.slug}/',
                reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            ),
            (
                f'/profile/{self.user}/',
                reverse('posts:profile', args=[self.user.username]),
            ),
            (
                f'/posts/{self.post.id}/',
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            ),
            ('/create/', reverse('posts:post_create')),
            (
                f'/posts/{self.post.id}/edit/',
                reverse('posts:post_edit', args=[self.post.id]),
            ),
        ]

        for address, name in templates_address_names:
            with self.subTest(address=address):
                self.assertEqual(address, name)
