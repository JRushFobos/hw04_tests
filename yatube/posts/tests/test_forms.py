from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Вызывается один раз перед запуском всех тестов класса.'''
        super().setUpClass()
        # cls.user = User.objects.create_user(username='Автор Мокрушин')
        cls.author = User.objects.create_user(
            username='Мокрушин',
            first_name='Евгений',
            last_name='Мокрушин',
            email='fobos_media@mail.ru',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста для формы',
            group=cls.group,
        )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_form_create(self):
        '''Проверка создания нового поста, авторизированным пользователем'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст поста для формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args={self.author.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст поста для формы',
                group=TestCreateForm.group,
            ).exists()
        )

    def test_form_update(self):
        '''Проверка редактирования поста через форму на странице.'''
        url = reverse('posts:post_edit', args={self.post.pk})
        self.authorized_client.get(url)
        # Инфо для изменения текста поста
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст поста',
        }
        # Отправляем POST запрос на изменения текста поста
        self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.pk}),
            data=form_data,
            follow=True,
        )
        # Проверяем что запись с измененным текстом поста сохранилась
        self.assertTrue(
            Post.objects.filter(
                text='Обновленный текст поста', group=TestCreateForm.group
            ).exists()
        )
