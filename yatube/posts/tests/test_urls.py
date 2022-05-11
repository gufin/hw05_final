from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Post, Group, User

URL_HOME = 'posts/index.html'
URL_GROUP_LIST = 'posts/group_list.html'
URL_PROFILE = 'posts/profile.html'
URL_POST_DETAIL = 'posts/post_detail.html'
URL_POST_CRATE = 'posts/create_post.html'


class StaticURLTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='HasNoName')
        Post.objects.create(
            text='Тестовый текст',
            author_id=author.id,
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

        cls.templates_url_names = {
            URL_HOME: ['/'],
            URL_GROUP_LIST: ['/group/test/'],
            URL_PROFILE: ['/profile/HasNoName/'],
            URL_POST_DETAIL: ['/posts/1/'],
            URL_POST_CRATE: ['/posts/1/edit/', '/create/'],
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.filter(id=1)[0]
        self.user2 = User.objects.create_user(username='HasNoName2')
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)

    def test_url_exists_at_desired_location(self):
        """Проверка доступности страниц по правам"""
        urls_for_test = {
            '/': 'all',
            '/group/test/': 'all',
            '/profile/HasNoName/': 'all',
            '/posts/1/': 'all',
            '/posts/1/edit/': 'author',
            '/create/': 'auth',
            '/unexisting_page/': 'not_found',
        }
        for url in urls_for_test:
            with self.subTest(url=url):
                if urls_for_test[url] == 'all':
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif urls_for_test[url] == 'auth':
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif urls_for_test[url] == 'author':
                    response = self.authorized_client2.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, addresses in self.templates_url_names.items():
            for address in addresses:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
