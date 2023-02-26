from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
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

    def test_404_url_exists_at_desired_location(self):
        '''Страница /unexisting.page 404 доступна любому пользователю.'''
        response = self.guest_client.get('/unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверки для не авторизованного пользователя
    def test_urls_correct_status_code_template_non_aut(self):
        '''Тесты статусов ответов и шаблонов неавторизированного
        пользователя.
        '''
        templates_url_names = [
            ('/', 'posts/index.html', HTTPStatus.OK),
            (
                f'/group/{self.group.slug}/',
                'posts/group_list.html',
                HTTPStatus.OK,
            ),
            (f'/profile/{self.user}/', 'posts/profile.html', HTTPStatus.OK),
            (
                f'/posts/{self.post.id}/',
                'posts/post_detail.html',
                HTTPStatus.OK,
            ),
            ('/about/tech/', 'about/tech.html', HTTPStatus.OK),
            ('/about/author/', 'about/author.html', HTTPStatus.OK),
            ('/auth/login/', 'users/login.html', HTTPStatus.OK),
        ]

        for address, template, code in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница /posts/<post_id>/edit/ доступна любому пользователю.'''
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/')
        )

    def test_post_create_url_exists_at_desired_location(self):
        '''Страница /create/ доступна любому пользователю.'''
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_urls_correct_status_code_template_auth(self):
        '''Тесты статусов ответов и шаблонов авторизированного пользователя.'''
        templates_url_names = [
            (
                f'/posts/{self.post.id}/edit/',
                'posts/create_post.html',
                HTTPStatus.OK,
            ),
            ('/create/', 'posts/create_post.html', HTTPStatus.OK),
            (
                '/auth/password_change/',
                'users/password_change_form.html',
                HTTPStatus.OK,
            ),
            (
                '/auth/password_reset/',
                'users/password_reset_form.html',
                HTTPStatus.OK,
            ),
            ('/auth/logout/', 'users/logged_out.html', HTTPStatus.OK),
        ]

        for address, template, code in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)
                self.assertTemplateUsed(response, template)

    def test_about_tech_url_exists_at_desired_location(self):
        '''Страница / доступна любому пользователю.'''
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
