import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author_id=author.id,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

        cls.group2 = Group.objects.create(
            title='Тестовая группа',
            slug='test2',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.filter(id=1)[0]
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_Post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'HasNoName'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый текст',
            ).exists()
        )

    def test_edit_Post(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group2.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
        )
        post = get_object_or_404(Post, id=1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(post.author, self.user)

    def test_create_post_with_image(self):
        """при отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        group = get_object_or_404(Group, id=1)
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
            'group': group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = get_object_or_404(Post, id=posts_count + 1)
        response = self.guest_client.get(reverse('posts:index'))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

    def test_comment_create(self):
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий'}
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
