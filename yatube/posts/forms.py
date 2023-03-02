from django import forms

from .models import Comment, Group, Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Напишите текст поста',
            'group': 'Выберите группу (если хотите)',
            'image': 'Добавьте картинку (если хотите)',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Напишите текст комментария'}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo', 'bio')
        help_texts = {
            'photo': 'Добавьте фото профиля',
            'bio': 'Напишите пару слов о себе, цитату или что-то ещё'
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')
        help_texts = {
            'title': 'Напишите название группы',
            'slug': ('Напишите короткое имя группы латиницей без пробелов. '
                     'Это имя будет отображаться в URL'),
            'description': 'Слоган или описание группы'
        }
