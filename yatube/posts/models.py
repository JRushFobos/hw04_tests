from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Тест', help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    class Meta:
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
        ordering = ('-pub_date',)

    def __str__(self):
        '''Возвращает строковое представление модели'''
        return self.text


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        help_text='200 characters max.',
        verbose_name='Заголовок',
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группы'

    def __str__(self):
        '''Возвращает строковое представление модели'''
        return self.title
