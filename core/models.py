from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=200)
    subheader = models.CharField(max_length=200, blank=True)
    progress = models.IntegerField()
    end_date = models.DateField()
    participants = models.ManyToManyField(Participant, related_name='projects')

    def __str__(self):
        return self.title

class News(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    read_time = models.CharField(max_length=50)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(News, self).save(*args, **kwargs)