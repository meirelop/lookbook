import json
from django.db import models
from django.utils import timezone

#
# class ScrapyItem(models.Model):
#     unique_id = models.CharField(max_length=100, null=True)
#     data = models.TextField()  # this stands for our crawled data
#     date = models.DateTimeField(default=timezone.now)
#
#     # This is for basic and custom serialisation to return it to client as a JSON.
#     @property
#     def to_dict(self):
#         data = {
#             'data': json.loads(self.data),
#             'date': self.date
#         }
#         return data
#
#     def __str__(self):
#         return self.unique_id



class TimestampedModel(models.Model):
    """
        An abstract base class model that provides
        self-updating ``created`` and ``modified`` fields.
    """
    created_django = models.DateTimeField(auto_now_add=True)
    modified_django = models.DateTimeField(auto_now=True)

    class Meta:
        # abstract True to prevent creating unnecessary tables in db
        abstract = True


class Look(TimestampedModel):
    img_url     = models.URLField('Location of look img', max_length=2000)
    full_id     = models.TextField('Look full ID', blank=True)
    look_id     = models.IntegerField('Lookbook id')
    # look_id = models.IntegerField('Lookbook id', unique=True)
    hype        = models.IntegerField('Hype rating', default=0)
    created     = models.DateTimeField('Creation date', default=timezone.now, blank=True)
    country     = models.TextField('Country')
    hashtags    = models.TextField('Hashtags contained')

    def __str__(self):
        return 'Look %s (%s)' % (self.id, self.img_url)