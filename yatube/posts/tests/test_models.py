from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    user = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст который занимает больше пятнадцати символов'
        )

    def test_models_have_correct_object_names(self):
        """text в posts и gorup совпадает с ожидаемым."""
        correct_answer = self.post.text[:15]
        self.assertEqual(str(self.post), correct_answer)
        correct_answer_for_group = self.group.slug
        self.assertEqual(str(self.group.slug), correct_answer_for_group)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Адрес для страницы с группой',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Пожалуйста напишите хоть что нибудь',
            'group': 'Можно и не заполнять',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
