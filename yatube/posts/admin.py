from django.contrib import admin

from .models import Group, Post, Follow


class PostAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    search_fields = ('description',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'
    list_display = (
        'id',
        'title',
        'description',
        'slug',
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
