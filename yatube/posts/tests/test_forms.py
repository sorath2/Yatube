import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse

from http import HTTPStatus

from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        '''Проверка записи созданного поста в базе данных'''
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {'text': 'Тестовый пост в форме',
                     'group': self.group.id,
                     'image': uploaded,
                     }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         'Пост не добавлен в базу данных')
        self.assertTrue(Post.objects.filter(
                        text='Тестовый пост в форме',
                        group=self.group.id,
                        author=self.user,
                        image='posts/small2.gif'
                        ).exists(), 'Ошибка при создании поста')

    def test_edit_post(self):
        '''Проверка факта изменения поста в базе данных при редактировании'''
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {'text': 'Тестовый пост в форме',
                     'group': self.group.id,
                     'image': uploaded,
                     }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.text, 'Тестовый пост в форме')
        self.assertEqual(Post.objects.count(),
                         posts_count)


class CommentFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
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
        cls.comment = Comment.objects.create(
            post_id=cls.post.id,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_authorized_user_only_comment(self):
        '''Проверка возможности комментировать посты
            только авторизованным пользователем'''
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий'}
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data, follow=True
        )
        self.assertEqual(response_guest.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(),
                            comment_count + 1,
                            'Ошибочно добавленный комментарий')
        response_auth = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data, follow=True
        )
        self.assertEqual(response_auth.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(),
                         comment_count + 1,
                         'Комментарий не добавился')

    def test_create_comment_in_post_detail_page(self):
        '''Проверка что комментарий появляется на странице поста'''
        response_comment = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        comment = response_comment.context['comments']
        self.assertIn(self.comment, comment,
                      'Комментария нет на странице поста')
