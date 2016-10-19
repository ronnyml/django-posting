# -*- encoding: utf-8 -*-

import io
from PIL import Image

from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile


def generate_thumb(img, thumb_size, format):
    img.seek(0)
    image = Image.open(img)

    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')

    thumb_w, thumb_h = thumb_size
    image2 = image
    image2.thumbnail(thumb_size, Image.ANTIALIAS)    

    io2 = io.BytesIO()
    if format.upper() =='JPG':
        format = 'JPEG'

    image2.save(io2, format)
    return ContentFile(io2.getvalue())

class ImageWithThumbsFieldFile(ImageFieldFile):
    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)

        if self.field.sizes:
            def get_size(self, size):
                if not self:
                    return ''
                else:
                    split = self.url.rsplit('.', 1)
                    thumb_url = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                    return thumb_url

            for size in self.field.sizes:
                (w, h) = size
                setattr(self, 'url_%sx%s' % (w, h), get_size(self, size))

    def save(self, name, content, save=True):
        super(ImageWithThumbsFieldFile, self).save(name, content, save)

        if self.field.sizes:
            for size in self.field.sizes:
                (w, h) = size
                split = self.name.rsplit('.', 1)
                thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                thumb_content = generate_thumb(content, size, split[1])
                thumb_name_ = self.storage.save(thumb_name, thumb_content)

                if not thumb_name == thumb_name_:
                    raise ValueError('There is already %s' % thumb_name)

    def delete(self, save=True):
        name = self.name
        super(ImageWithThumbsFieldFile, self).delete(save)
        if self.field.sizes:
            for size in self.field.sizes:
                (w, h) = size
                split = name.rsplit('.', 1)
                thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                try:
                    self.storage.delete(thumb_name)
                except:
                    pass

class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile
    def __init__(self, verbose_name=None, name=None, width_field=None, 
         height_field=None, sizes=None, **kwargs):
        self.verbose_name = verbose_name
        self.name = name
        self.width_field = width_field
        self.height_field = height_field
        self.sizes = sizes
        super(ImageField, self).__init__(**kwargs)
        