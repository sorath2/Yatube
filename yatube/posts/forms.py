from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа'),
            'image': _('Картинка'),
        }
        help_texts = {
            'text': _('Текст нового поста'),
            'group': _('Группа, к которой будет относиться пост'),
            'image': _('Картинка, которую можно прикрепить к посту'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': _('Текст комментария'),
        }
        help_texts = {
            'text': _('Текст нового комментария'),
        }
