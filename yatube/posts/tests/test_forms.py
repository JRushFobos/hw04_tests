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
            text='Тестовый текст поста',
            group=cls.group,
        )

    def setUp(self):
        '''Подготовка прогона теста. Вызывается перед каждым тестом.'''
        self.authorized_client = Client()
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
            response,
            reverse('posts:profile', args=[self.post.author.username]),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        object = Post.objects.all().first()
        self.assertEqual(object.text, form_data['text'])
        self.assertEqual(object.group.id, form_data['group'])
        self.assertEqual(object.author, self.post.author)

    def test_form_update(self):
        '''Проверка редактирования поста через форму на странице.'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст поста',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=form_data,
            follow=True,
        )
        object = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(object.text, form_data['text'])
        self.assertEqual(object.group.id, form_data['group'])
        self.assertEqual(object.author, self.post.author)
        self.assertEqual(Post.objects.count(), post_count)
