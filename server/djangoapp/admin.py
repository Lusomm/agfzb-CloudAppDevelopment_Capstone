from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel


# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1
    
class CarModelAdmin(admin.ModelAdmin):
    model = CarModel
    
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]

# CarModelAdmin class

# CarMakeAdmin class with CarModelInline

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
