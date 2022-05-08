from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    """Group of posters calss"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес для страницы с группой')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = "group"

    def __str__(self):
        return self.slug


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Пожалуйста напишите хоть что нибудь')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name='posts',
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Можно и не заполнять'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "post"

    def __str__(self):
        count_of_simbols = 15
        return self.text[:count_of_simbols]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE,
                             verbose_name='Пост')
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE,
                               verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Напишите комментарий')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата')


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
