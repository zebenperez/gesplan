from django.contrib import admin

from .models import *


class AgreementTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)

class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'rol', 'company')
    list_filter = ('rol',)
    search_fields = ('name', 'surname', 'nif', 'company__name', 'company__nif')

class EmployeeAccessLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'location', 'finish')

class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)

class FacilityAdmin(admin.ModelAdmin):
    list_display = ('description', 'code')

class FacilityTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'order', 'operation_time', 'dashboard')

class FacilityActionsAdmin(admin.ModelAdmin):
    list_display = ('date', 'driver', 'fa_type', 'facility', 'truck')

class FacilityActionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

class FacilityManteinanceConceptAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

class FacilityManteinanceStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name',)

#class PriorityAdmin(admin.ModelAdmin):
#    list_display = ('code', 'weight', 'description')

class TrayAdmin(admin.ModelAdmin):
    list_display = ('number',)

class TrayTrackingAdmin(admin.ModelAdmin):
    list_display = ('tray', 'ini_date', 'end_date', 'source', 'target', 'finish')

class TruckTypeAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year')

class TruckManteinanceConceptAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

class TruckManteinanceStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

class FacilityWasteManagerTabular(admin.TabularInline):
    model = FacilityWasteManager
    extra = 1

class WasteAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'external_manager')
    inlines = [FacilityWasteManagerTabular,]

class WasteInFacilityAdmin(admin.ModelAdmin):
    list_display = ('code', 'facility', 'waste', 'filling_degree', 'toRoute')
    list_filter = ('facility',)

admin.site.register(AgreementType, AgreementTypeAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(ContractType, ContractTypeAdmin)
admin.site.register(Company)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeAccessLog, EmployeeAccessLogAdmin)
admin.site.register(EmployeeType, EmployeeTypeAdmin)
admin.site.register(EmployeeTruck)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(FacilityType, FacilityTypeAdmin)
admin.site.register(FacilityActions, FacilityActionsAdmin)
admin.site.register(FacilityActionType, FacilityActionTypeAdmin)
admin.site.register(FacilityManteinanceConcept, FacilityManteinanceConceptAdmin)
admin.site.register(FacilityManteinanceStatus, FacilityManteinanceStatusAdmin)
admin.site.register(FacilityManteinanceImage)
admin.site.register(Item, ItemAdmin)
admin.site.register(Route)
admin.site.register(RouteMpl)
admin.site.register(RouteMplPoint)
admin.site.register(RouteExt)
admin.site.register(Tray, TrayAdmin)
admin.site.register(TrayTracking, TrayTrackingAdmin)
admin.site.register(Truck)
admin.site.register(TruckType, TruckTypeAdmin)
admin.site.register(TruckManteinanceConcept, TruckManteinanceConceptAdmin)
admin.site.register(TruckManteinanceStatus, TruckManteinanceStatusAdmin)
admin.site.register(UnitType)
admin.site.register(Waste, WasteAdmin)
#admin.site.register(Priority, PriorityAdmin)
admin.site.register(WasteInFacility, WasteInFacilityAdmin)
