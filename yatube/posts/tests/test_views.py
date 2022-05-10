from django import forms
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User, Follow
from ..utills import paginator_add


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='HasNoName')
        cls.author2 = User.objects.create_user(username='HasNoName2')
        Post.objects.create(
            text='Тестовый текст',
            author_id=author.id,
        )
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

        Group.objects.create(
            title='Тестовая группа2',
            slug='test2',
            description='Тестовое описание2',
        )

        for i in range(1, 14):
            post_text = f'Тестовый текст {i}'
            Post.objects.create(
                text=post_text,
                author_id=author.id,
                group_id=group.id
            )

        cls.templates_page_names = {
            'posts/index.html': [reverse('posts:index')],
            'posts/group_list.html':
                [reverse('posts:group_list', kwargs={'slug': 'test'})],
            'posts/profile.html':
                [reverse('posts:profile', kwargs={'username': 'HasNoName'})],
            'posts/post_detail.html':
                [reverse('posts:post_detail', kwargs={'post_id': 1})],
            'posts/create_post.html': [
                reverse('posts:post_create'),
                reverse('posts:post_edit', kwargs={'post_id': 1})
            ],
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.filter(id=1)[0]
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user2 = User.objects.filter(id=2)[0]
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_names in self.templates_page_names.items():
            for reverse_name in reverse_names:
                with self.subTest(template=template):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и пдажинатор
        выводит 10 постов на странице."""
        response = self.guest_client.get(reverse('posts:index'))

        post_list = Post.objects.select_related('author').all()
        page_obj = paginator_add(post_list, 10).object_list
        expected = list(page_obj)

        testing_data = response.context['page_obj'].object_list
        self.assertEqual(testing_data, expected)

    def test_second_index_page_contains_four_records(self):
        """Пдажинатор выводит 4 поста на 2 странице index."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом и пдажинатор
                выводит 10 постов на странице."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))

        group = get_object_or_404(Group, slug='test')
        posts = group.posts.all()
        expected = list(paginator_add(posts, 10).object_list)
        testing_data = response.context['page_obj'].object_list
        self.assertEqual(testing_data, expected)

    def test_second_group_list_page_contains_three_records(self):
        """Пдажинатор выводит 3 поста на 2 странице group_list."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом и пдажинатор
                        выводит 10 постов на странице."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))

        author = get_object_or_404(User, username='HasNoName')
        posts = Post.objects.select_related('author').filter(
            author_id=author.id)
        expected = list(paginator_add(posts, 10).object_list)
        testing_data = response.context['page_obj'].object_list
        self.assertEqual(testing_data, expected)

    def test_second_profile_page_contains_four_records(self):
        """Пдажинатор выводит 4 постов на 2 странице group_list."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_post_detail_correct_context(self):
        """Детальная страница поста сформирована с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))

        post = get_object_or_404(Post, id=1)
        testing_data = response.context['post']
        self.assertEqual(testing_data, post)

    def test_create_post_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        """Страница редактирования поста сформирована
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        post = get_object_or_404(Post, id=1)

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertContains(response, post.text)

    def test_post_in_correct_place_in_index(self):
        """После создания поста, он появляется в нужном месте
        на галвной странице."""
        post = Post.objects.create(
            text='Этот пост мы ждем на главной странице',
            author_id=1,
        )
        response = self.guest_client.get(reverse('posts:index'))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

    def test_post_in_correct_place_in_group_list(self):
        """После создания поста, он появляется в нужном месте
            на странице группы и не в группе для которой не предназанчен."""
        post = Post.objects.create(
            text='Этот пост мы ждем на странице группы',
            author_id=1,
            group_id=1,
        )
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'}))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test2'}))
        testing_data = len(response.context['page_obj'].object_list)
        self.assertEqual(testing_data, 0)

    def test_post_in_correct_place_in_profile(self):
        """После создания поста, он появляется в нужном месте
                        на странице профиля."""
        post = Post.objects.create(
            text='Этот пост мы ждем на странице группы',
            author_id=1,
            group_id=1,
        )
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)

    def test_cache_in_index(self):
        """Проверка работы кэширования списка постов главной страницы"""
        post = Post.objects.create(
            text='Этот пост мы ждем на главной странице',
            author_id=1,
        )
        response = self.guest_client.get(reverse('posts:index'))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)
        post.delete()
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data.text,
                         'Этот пост мы ждем на главной странице')

    def test_following(self):
        """Проверка работы подписки"""
        self.authorized_client2.get(reverse('posts:profile_follow',
                                    kwargs={'username': 'HasNoName'}))
        following = Follow.objects.filter(
            user_id=self.user2.id,
            author_id=self.user.id,
        ).exists()
        self.assertTrue(following)

    def test_post_of_followed_author_in_correct_place(self):
        self.authorized_client2.get(reverse('posts:profile_follow',
                                            kwargs={'username': 'HasNoName'}))
        post = Post.objects.create(
            text='Проверка работы подписки',
            author_id=self.user.id,
        )
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        testing_data = response.context['page_obj'].object_list[0]
        self.assertEqual(testing_data, post)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        testing_data = response.context['page_obj'].object_list
        self.assertEqual(len(testing_data), 0)
