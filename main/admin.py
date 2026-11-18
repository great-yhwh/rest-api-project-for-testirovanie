from django.contrib import admin

from main.models import Constellation, Star, Planet, ObservationLog

admin.site.register(Constellation)
admin.site.register(Star)
admin.site.register(Planet)
admin.site.register(ObservationLog)
