from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.text import slugify


def upload_location(instance, filename):
    return '%s/%s' % (instance.id, filename)

class PostManager(models.Manager):
    def get_query_set(self):
        super(PostManager, self).get_query_set().filter(draft=False).filter(publish__lte=timezone.now())

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-created', '-updated']    
            

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)
