from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.another_user = User.objects.create_user(
            username='Миллер',
            first_name='Евгений',
            last_name='Мокрушин',
            email='fobos_media@mail.ru',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.another_user)

    def test_status_code_template_non_auth_and_auth(self):
        '''Тесты статусов ответов и шаблонов неавторизированного и
        авторизированного пользователя.
        '''
        templates_url_names = [
            (reverse('posts:index'), HTTPStatus.OK, self.guest_client),
            (
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse('posts:profile', kwargs={'username': self.user}),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (reverse('about:tech'), HTTPStatus.OK, self.guest_client),
            (reverse('about:author'), HTTPStatus.OK, self.guest_client),
            (reverse('users:login'), HTTPStatus.OK, self.guest_client),
            (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                reverse('posts:post_create'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                reverse('users:password_change'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                reverse('users:password_reset_form'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (reverse('users:logout'), HTTPStatus.OK, self.authorized_client),
            ('/unexisting_page', HTTPStatus.NOT_FOUND, self.guest_client),
        ]

        for address, code, auth in templates_url_names:
            with self.subTest(address=address):
                if auth == self.authorized_client:
                    response = self.authorized_client.get(address)
                else:
                    response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_status_code_template(self):
        '''Тесты шаблонов пользователя.'''
        templates_url_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                'posts/group_list.html',
            ),
            (
                reverse('posts:profile', kwargs={'username': self.user}),
                'posts/profile.html',
            ),
            (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
                'posts/post_detail.html',
            ),
            (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
                'posts/create_post.html',
            ),
            (
                reverse('posts:post_create'),
                'posts/create_post.html',
            ),
            (
                reverse('users:password_change'),
                'users/password_change_form.html',
            ),
            (
                reverse('users:password_reset_form'),
                'users/password_reset_form.html',
            ),
            (reverse('users:logout'), 'users/logged_out.html'),
        )

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница /posts/<post_id>/edit/ доступна любому пользователю.'''
        addresses = (
            (
                (
                    self.guest_client.get(
                        reverse(
                            'posts:post_edit', kwargs={'post_id': self.post.id}
                        )
                    )
                ),
                (f'/auth/login/?next=/posts/{self.post.id}/edit/'),
            ),
            (
                (
                    self.authorized_client2.get(
                        reverse(
                            'posts:post_edit',
                            kwargs={'post_id': self.post.id},
                        )
                    )
                ),
                (f'/posts/{self.post.id}/'),
            ),
        )

        for address, redirect in addresses:
            with self.subTest(address=address):
                self.assertRedirects(address, redirect)

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
