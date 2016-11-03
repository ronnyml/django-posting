from django.contrib import admin

from .models import Category, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'slug', 'posts_count', 'thumbnail', 'active'
    ]
    list_filter = ['active']
    search_fields = ['title']

    def posts_count(self, obj):
        count = Post.objects.filter(category_id=obj.id).count()
        return count

    posts_count.allow_tags = True
    posts_count.short_description = 'No. Posts'

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created', 'updated']
    list_display_links = ['created']
    list_editable = ['title']
    list_filter = ['created', 'updated']
    search_fields = ['title', 'content']

    class Meta:
        model = Post


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
