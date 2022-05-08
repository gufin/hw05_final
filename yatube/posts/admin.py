from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
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
    list_display = ('id', 'title', 'description', 'slug')
    search_fields = ('description',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'
    list_display = (
        'id',
        'title',
        'description',
        'slug',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
