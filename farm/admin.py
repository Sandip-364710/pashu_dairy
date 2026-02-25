from django.contrib import admin
from .models import CustomUser, Animal, MilkRecord


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'village', 'date_joined']
    search_fields = ['name', 'mobile', 'village']
    list_filter = ['date_joined']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_no', 'animal_type', 'breed', 'insemination_date', 'checkup_status', 'owner']
    search_fields = ['tag_no', 'owner__name']
    list_filter = ['animal_type', 'breed', 'checkup_status', 'insemination_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MilkRecord)
class MilkRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'liters', 'price_per_liter', 'total_amount']
    search_fields = ['animal__tag_no', 'animal__owner__name']
    list_filter = ['date', 'animal__animal_type']
    readonly_fields = ['total_amount', 'created_at']
