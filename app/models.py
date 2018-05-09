from django.db import models

class ImageTest(models.Model):
    image = models.ImageField(upload_to='app')
    image_url = models.URLField(blank=True)
