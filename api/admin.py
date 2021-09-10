from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('genre', 'slug')
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    search_fields = ('title', 'year')
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'text')
    search_fields = ('title', 'author', 'text')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'author', 'text')
    search_fields = ('review', 'author', 'text')
    empty_value_display = '-пусто-'


admin.site.register(User)
admin.site.register(Category, CategoriesAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
