from django.apps import apps
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from django.utils.text import slugify

from utils.image_thumbs import ImageWithThumbsField


def upload_location(instance, filename):
    return '%s/%s' % (instance.id, filename)

class PostManager(models.Manager):
    def get_query_set(self):
        super(PostManager, self).get_query_set().filter(draft=False).filter(publish__lte=timezone.now())

class Category(models.Model):
    title  = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    image = ImageWithThumbsField(
        blank=True,
        upload_to=upload_location,
        sizes=((300, 200), (200, 130))
    )
    status = models.BooleanField(default=True, verbose_name='Active')
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']

    def __str__(self):
        return self.title

    def thumbnail(self):
        if self.image != '':
            image_url = self.image.url_300x200
            return "<img src='%s' />" % (image_url)
        else:
            return ''
    thumbnail.short_description = 'Image'
    thumbnail.allow_tags = True

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(null=True, blank=True, 
            width_field='width', 
            height_field='height',
            upload_to=upload_location)
    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    objects = PostManager()

    class Meta:
        ordering = ['-created', '-updated']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'slug': self.slug})

class Hashtag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Hashtag')
    posts = models.ManyToManyField(Post)
    categories = models.ManyToManyField(Category, blank=True)
    date_added = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    app_name = instance._meta.app_label
    model_name = instance._meta.object_name
    Model = apps.get_model('{}.{}'.format(app_name, model_name))
    qs = Model.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

def post_save_post_receiver(sender, instance, *args, **kwargs):
    if instance.content:
        final_text = ' '.join(instance.content.split())
        words = final_text.split(' ')
        for word in words:
            if word[0] == '#':
                word = word.replace('#' , '')
                hashtag, created = Hashtag.objects.get_or_create(name=word)
                hashtag.posts.add(instance.id)
                hashtag.categories.add(instance.category.id)

pre_save.connect(pre_save_post_receiver, sender=Category)
pre_save.connect(pre_save_post_receiver, sender=Post)
post_save.connect(post_save_post_receiver, sender=Post)
