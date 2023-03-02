from django.contrib import admin

from .models import Comment, Follow, Group, Post, Profile
from .utils import get_all_fields


class GroupAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Group)
    search_fields = ('title', 'slug')


class PostAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Post)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Comment)


class FollowAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Follow)


class ProfileAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Profile)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
