from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(PublisherSubscription)
admin.site.register(JournalistSubscription)
