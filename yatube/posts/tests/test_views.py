import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django import forms

from ..models import Post, Group, Follow

User = get_user_model()
QUANTITY_OF_TEST_POSTS = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост #0',
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
                        'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
                        'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text_0, 'Тестовый пост #0')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text_0, 'Тестовый пост #0')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text_0, 'Тестовый пост #0')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        post_0 = {response.context['post'].text: 'Тестовый пост #0',
                  response.context['post'].group: self.group,
                  response.context['post'].author: self.user,
                  response.context['post'].image: 'posts/small.gif'
                  }
        for value, expected in post_0.items():
            self.assertEqual(value, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_correctly_created(self):
        """Пост при создании отображается на корректных страницах"""
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index, 'Поста нет на главной странице')
        self.assertIn(self.post, group, 'Поста нет в странице профиля')
        self.assertIn(self.post, profile, 'Поста нет в странице группы')

    def test_post_not_added_in_wrong_group(self):
        """Пост при создании не попал в группу,
            для которой не был предназначен"""
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug 2',
            description='Тестовое описание 2',
        )
        post_group2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост группы 2',
            group=group2,
        )
        response_group = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}))
        group1 = response_group.context['page_obj']
        self.assertNotIn(post_group2, group1,
                         'Поста нет в другой группе')

    def test_cache_index_page(self):
        '''Проверка кэширования страницы index'''
        first_responce = self.authorized_client.get(
            reverse('posts:index')
        )
        first_page = first_responce.content
        Post.objects.create(
            author=self.user,
            text='Проверка кэша',
            group=self.group)
        second_responce = self.authorized_client.get(reverse('posts:index'))
        second_page = second_responce.content
        self.assertEqual(second_page, first_page)
        cache.clear()
        after_clear_cache_responce = self.authorized_client.get(
            reverse('posts:index')
        )
        third_page = after_clear_cache_responce.content
        self.assertNotEqual(third_page, first_page)


class PaginatorViewsTests(TestCase):
    QUANTITY_OF_TEST_POSTS_FIRST_PAGE = 10
    QUANTITY_OF_TEST_POSTS_SECOND_PAGE = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cache.clear()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        test_posts = []
        for i in range(QUANTITY_OF_TEST_POSTS):
            test_posts.append(Post(
                text=f'Тестовый пост #{i}',
                group=cls.group,
                author=cls.user
            ))
        cls.post = Post.objects.bulk_create(test_posts)
        cls.pages = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}),
            reverse('posts:profile',
                    kwargs={'username': f'{cls.user.username}'})
        ]

    def test_pages_contains_ten_records(self):
        '''Проверка количества постов на первой странице.'''
        for page in self.pages:
            response = self.authorized_client.get(page)
            self.assertEqual(
                len(response.context['page_obj']),
                self.QUANTITY_OF_TEST_POSTS_FIRST_PAGE,
                f'Ошибка в кол-ве постов на странице {page}'
            )

    def test_pages_contains_three_records(self):
        '''Проверка количества постов на второй странице.'''
        for page in self.pages:
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                self.QUANTITY_OF_TEST_POSTS_SECOND_PAGE,
                f'Ошибка в кол-ве постов на странице {page}'
            )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.user3 = User.objects.create_user(username='auth3')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)

    def test_auth_user_follow_unfollow_other_users(self):
        """Авторизованный пользователь может подписываться
            на других пользователей и удалять их из подписок"""
        count_follow = Follow.objects.filter(user=self.user).count()
        Follow.objects.create(user=self.user, author=self.user3)
        count_follow_new = Follow.objects.filter(user=self.user).count()
        self.assertEqual(count_follow + 1, count_follow_new)
        Follow.objects.filter(user=self.user, author=self.user3).delete()
        count_follow_new = Follow.objects.filter(user=self.user).count()
        self.assertEqual(count_follow, count_follow_new)

    def test_follower_see_new_post_(self):
        """Новая запись пользователя появляется в ленте тех,
            кто на него подписан и не появляется в ленте тех,
            кто не подписан"""
        new_post_following = Post.objects.create(
            author=self.user2, text='Новый пост автора')
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        follower_page = response_follower.context['page_obj']
        response_unfollower = self.authorized_client3.get(
            reverse('posts:follow_index'))
        unfollower_page = response_unfollower.context['page_obj']
        self.assertIn(new_post_following, follower_page)
        self.assertNotIn(new_post_following, unfollower_page)
