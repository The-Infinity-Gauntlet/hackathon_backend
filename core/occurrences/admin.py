from django.contrib import admin
from core.occurrences.infra.models import Occurrence

@admin.register(Occurrence)
class Occurrence(admin.ModelAdmin):
    list_display = ('date', 'neighborhood')