from django.contrib import admin
from django.db.models import Count

from .models import Category, Hashtag, Post


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
    list_display = [
        'title', 'hashtags', 'category', 'created', 'draft'
    ]
    list_display_links = ['created']
    list_editable = ['title']
    list_filter = ['category', 'is_featured', 'created', 'updated']
    search_fields = ['title', 'content']

    class Meta:
        model = Post

    def hashtags(self, obj):
        words = ''
        for word in Hashtag.objects.filter(posts=obj.id):
            words += '#' + word.name + ' '
        return u'<strong>%s</strong>' % words
    hashtags.allow_tags = True

class HashtagAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'hashtags_count', 'related_categories', 'date_added'
    ]
    list_filter = (
        ('categories', admin.RelatedOnlyFieldListFilter),
    )
    ordering = ['categories__title', 'name']

    def hashtags_count(self, obj):
        count = Hashtag.objects.filter(id=obj.id).annotate(Count('posts'))
        count = count[0].posts__count
        return count
    hashtags_count.allow_tags = True
    hashtags_count.short_description = 'No. Posts'

    def related_categories(self, obj):
        answers = ''
        for c in Category.objects.filter(hashtag__id=obj.id).distinct():
            answers += '-' + c.title + '  '

        return answers
    related_categories.short_description = 'Categories'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Hashtag, HashtagAdmin)
admin.site.register(Post, PostAdmin)
