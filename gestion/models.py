from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Avg, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _ 

import django.utils.timezone as tz
import datetime, hashlib, random, string

from gestion.route_lib import route_to_json
from gestion.email_lib import send_warning_level_email


class Config(models.Model):
    key = models.CharField(max_length=200, verbose_name = _('clave'))
    value = models.TextField(verbose_name="valor")

    @staticmethod
    def get_value(key, default=""):
        try:
            config = Config.objects.get(key=key)
            return config.value
        except Exception as e:
            return ""

    @staticmethod
    def get_or_create_value(key):
        try:
            config, created = Config.objects.get_or_create(key=key)
            return config.value
        except Exception as e:
            print(e)
            return ""

    @staticmethod
    def set_value(key, value):
        config, created = Config.objects.get_or_create(key=key)
        config.value = value
        config.save()

    class Meta:
        verbose_name="Configuracion"
        verbose_name_plural = "Configuraciones"

'''
    COMPANIES
'''
class Company(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    register_number = models.IntegerField(verbose_name=_('Número de registro'), null=True, default=0)
    name = models.CharField(max_length=200, verbose_name = _('Razón Social'))
    #location = models.PointField(verbose_name = _('Dirección'), null=True)
    nif = models.CharField(max_length=20, null=True, unique=True, verbose_name=_('NIF'))
    phone = models.CharField(max_length=20, null=True, default = '0000000000', verbose_name = _('Teléfono de contacto'))
    email = models.EmailField(null=True, verbose_name = _('Email de contacto'))

    lat = models.CharField(max_length=50, verbose_name=_("Lat"), default="", null=True)
    lon = models.CharField(max_length=50, verbose_name=_("Lon"), default="", null=True)

    address = models.CharField(max_length=255, verbose_name='Dirección', default="", null=True, blank=True)
    cp = models.CharField(max_length=25, verbose_name='Postal Code', default="", null=True, blank=True)
    town = models.CharField(max_length=255, verbose_name='Municipio', default="", null=True, blank=True)
    province = models.CharField(max_length=255, verbose_name='Ciudad', default="", null=True, blank=True)

    def toJSON(self):
        company = { 'pk': self.pk, 'name': self.name}
        return company

    def get_facilities(self):
        items = list(Facility.objects.filter(company=self).distinct())
        fac_list = FacilityWasteManager.objects.filter(manager=self)
        for fac in fac_list:
            if fac.facility not in items:
                items.append(fac.facility)
        return items

    def __str__(self):
        try:
            return "%s - %s" % (self.nif, self.name)
        except:
            return ""

    class Meta:
        verbose_name = _('Empresa')
        verbose_name_plural = _('Empresas')

'''
    WASTE
'''
#class Priority(models.Model):
#    code = models.CharField(verbose_name=_('Código'), max_length=10, unique = True)
#    description = models.CharField(verbose_name = _('Descripción'), max_length=200, null = True)
#    weight = models.IntegerField(default=100, verbose_name= _('Peso'))
#
#    def toJSON(self):
#        priority = {'pk': self.pk, 'code': self.code, 'description': self.description, 'weight': self.weight}
#        return priority
#
#    class Meta:
#        verbose_name = _('Prioridad')
#        verbose_name_plural = _('Prioridades')
#        ordering = ['-weight']
#
#    def __str__(self):
#        return (self.code)

class UnitType(models.Model):
    code = models.CharField(verbose_name=_('Código'), max_length=10, default = 'Kg', unique = True)
    description = models.CharField(verbose_name = _('Descripción'), max_length=200, null = True)

    class Meta:
        verbose_name = _('Tipo de unidad')
        verbose_name_plural = _('Tipos de unidades')

    def __str__(self):
        return (self.code)

class WasteTreatment(models.Model):
    code = models.CharField(verbose_name=_('Código'), max_length=10, default='',blank=True, null=True)
    description = models.CharField(verbose_name = _('Descripción'), max_length=900, null=True)

    class Meta:
        verbose_name = _('Tratamiento del residuo')
        verbose_name_plural = _('Tratamientos de los residuos')

    def __str__(self):
        return (self.code)

class Waste(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    alert = models.BooleanField(default = False, verbose_name=_('Alertas'));
    dangerous = models.BooleanField(default = False, verbose_name=_('Peligroso'));
    ler = models.BigIntegerField(verbose_name='LER', unique=False, null=True)
    day_limit = models.FloatField(verbose_name=_('Límite diario'), blank=True, null=True, help_text=_("Límite diario de recogidas por usuario"))
    score = models.FloatField(verbose_name="Puntuacion", blank=True, null=True, default=-1)
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))
    description = models.CharField(max_length=200, verbose_name=_('Descripción'))
    recycle_text = models.TextField(verbose_name="Texto de Reciclaje", blank=True, null=True, help_text="Texto para fomentar la reutilizacion de residuos por parte del ciudadano")
    icon = models.ImageField(upload_to="icons/", verbose_name=_("Icono"), blank=True, null=True)

    units = models.ForeignKey(UnitType, verbose_name = _('Unidades'), on_delete=models.SET_NULL, null=True)
    #priority = models.ForeignKey(Priority, verbose_name=_('Prioridad'), on_delete=models.SET_NULL, null=False, default=1)
    external_manager = models.ForeignKey(Company, verbose_name=_("Gestor Externo"), on_delete=models.SET_NULL, blank=True, null=True)
    treatment = models.ForeignKey(WasteTreatment, verbose_name=_('Tratemiento'), on_delete=models.SET_NULL, null=True, blank=True)

    def toJSON(self):
        #waste = {'pk': self.id,  'ler': self.ler, 'name': self.name, 'description': self.description,
        #       'dangerous': self.dangerous, 'alert': self.alert, 'priority': self.priority.toJSON()}
        waste = {'pk': self.id,  'ler': self.ler, 'name': self.name, 'description': self.description,
               'dangerous': self.dangerous, 'alert': self.alert}
        return waste

    def __str__(self):
        return "%s [%s]" % (self.name, self.units.code)

    class Meta:
        verbose_name = 'Residuo'
        verbose_name_plural = 'Residuos'
        ordering = ['name']


'''
    FACILITIES
'''
class FacilityType(models.Model):
    dashboard = models.BooleanField(default=True, verbose_name=_('Ver en Dashboard'))
    order = models.IntegerField(default=1, verbose_name=_('Orden'))
    operation_time = models.IntegerField(default=20, verbose_name=_('Tiempo de operación (min)'))
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de instalación'
        verbose_name_plural = 'Tipos de instalación'
        ordering = ['order']

class Facility(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    #location = models.PointField(verbose_name = 'Localización')
    default_zoom = 15
    code = models.CharField(max_length=255, verbose_name='Código', null=True, default="")
    nima = models.CharField(max_length=50, verbose_name='NIMA', null=True, default="")
    description = models.CharField(max_length=255, verbose_name='Descripción', null=True, blank=True, default='')
    address = models.CharField(max_length=255, verbose_name='Dirección', default="", null=True, blank=True)
    town = models.CharField(max_length=255, verbose_name='Ciudad', default="", null=True, blank=True)
    #map_bubble_text = RichTextUploadingField(verbose_name="Ficha Burbuja", blank=True, null=True);

    lat = models.CharField(max_length=50, verbose_name=_("Lat"), default="", null=True, blank=True)
    lon = models.CharField(max_length=50, verbose_name=_("Lon"), default="", null=True, blank=True)

    company = models.ForeignKey(Company, verbose_name='Empresa gestora', on_delete=models.SET_NULL, null=True)
    company_owner = models.ForeignKey(Company,verbose_name='Empresa propietaria',on_delete=models.SET_NULL,null=True,related_name="facilities_owner")
    #fac_type = models.ForeignKey(FacilityType, null=True, blank=True, verbose_name=_('Tipo'))
    #priority = models.ForeignKey(Priority, verbose_name=_('Prioridad'), null=False, default=1)
    #download_point = models.ForeignKey('self', verbose_name='Punto de descarga', related_name='+', null=True, blank=True)

    #default_lon, default_lat = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), -101.193445, 19.702716)

    def toJSON(self):
        facility = {'pk': self.pk, 'code': self.code, 'nima': self.nima, 'description': self.description}
        return facility

    def __str__(self):
        return self.description

    def waste_by_filling_degree(self):
        i_list = self.waste.filter(toRoute=True).order_by("filling_degree", "waste")
        item_list = []
        current_waste = ""
        for item in i_list:
            if current_waste != item.waste.id:
                current_waste = item.waste.id
                item_list.append(item)
        return item_list

    @staticmethod
    def getPL():
        return Facility.objects.filter(description__contains="Punto")

    @staticmethod
    def getMPL():
        return Facility.objects.filter(code__startswith="MPL-")

    @staticmethod
    def getTargets():
        return Facility.objects.filter(description__contains="Planta")

    class Meta:
        verbose_name=_('Instalación')
        verbose_name_plural=_('Instalaciones')
        ordering=['description']

class WasteInFacility(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    show_user = models.BooleanField(verbose_name=_('Mostrar a usuarios'), default=True)
    toRoute = models.BooleanField(verbose_name=_('En ruta'), default=True)
    code = models.CharField(max_length=255, verbose_name='Código', default = "Cont.000")
    filling_degree = models.DecimalField(verbose_name = _('Porcentaje de llenado'), max_digits=5, decimal_places=2, default=0.)
    warning_filling_degree = models.DecimalField(verbose_name = _('Umbral de aviso'), max_digits = 5, decimal_places=2, default=45.)
    alert_filling_degree = models.DecimalField(verbose_name = _('Umbral de alerta'), max_digits = 5, decimal_places=2, default=80.)
    last_modification = models.DateTimeField(default=tz.now(), null=True, verbose_name=('Última modificación'), blank=True)

    advise_frec = models.IntegerField(verbose_name='Advise Frecuency', default=15, blank=True)
    emails = models.CharField(max_length=900, verbose_name='Emails', default="", blank=True)
    subject = models.CharField(max_length=900, verbose_name='Subject', default="", blank=True)
    body = models.TextField(verbose_name='Body', default="", blank=True)
    last_warning = models.DateTimeField(default=datetime.datetime.min, null=True, verbose_name=('Último aviso'))

    waste = models.ForeignKey(Waste, verbose_name = _('Residuo'), related_name = "facilities", on_delete=models.SET_NULL, null=True)
    facility = models.ForeignKey(Facility, verbose_name = _('Instalación'), related_name="waste", on_delete=models.CASCADE)
    download_point = models.ForeignKey(Facility, verbose_name=_('Punto de descarga'), related_name="download", on_delete=models.SET_NULL, null=True, default=None, blank=True)
    alt_download_point = models.ForeignKey(Facility, verbose_name = _('Descarga alternativo'), related_name="download_alt", on_delete=models.SET_NULL, null=True, default=None, blank=True)

#    def save(self, *args, **kwargs):
        #Si se supera el umbral de aviso y el residuo es voluminoso se envía una alerta
#        if self.warning and self.toRoute:
#            send_warning_level_email(["zebenperez@gmail.com"], self.waste.name, self.facility.description)
#        super(Event, self).save(*args, **kwargs)

    def toJSON(self):
        wif = {'pk': self.pk, 'to_route': self.toRoute, 'waste': self.waste.toJSON(), 'facility': self.facility.toJSON(),
              'filling_degree': self.filling_degree, 'warning_filling_degree': self.warning_filling_degree,
              'alert_filling_degree': self.alert_filling_degree}

        return wif

    def __str__(self):
        try:
            return "Contenedor de %s en %s" % (self.waste.name, self.facility.description)
        except:
            return self.code

    class Meta:
        verbose_name = _('Residuos en instalación')
        #unique_together = ('waste', 'facility', 'code')
        ordering = ['waste__code']

    def google_location(self):
        return self.facility.google_location()

    @property
    def alert(self):
        return ((self.alert_filling_degree <= self.filling_degree))

    @property
    def warning(self):
        return ((self.warning_filling_degree <= self.filling_degree))

    @property
    def external_manager(self):
        if self.waste != None and self.waste.external_manager != None:
            return self.waste.external_manager

        fwm = FacilityWasteManager.objects.filter(waste=self.waste, facility=self.facility).first()
        return fwm.manager if fwm != None else None

    def class_state(self):
        if self.alert:
            return "danger"
        else:
            if self.warning:
                return "warning"
            else:
                if self.filling_degree >= 1:
                    return "success"
        return "info"

@receiver(post_save, sender=WasteInFacility)
def send_warning_alert(sender, instance, **kwargs):
    #print("--1--")
    #print(instance.warning)
    #print(instance.toRoute)
    #Si se supera el umbral de aviso y el residuo es voluminoso se envía una alerta
    warning = instance.last_warning.strftime("%y-%m-%d %H:%M:%S")
    min_date = datetime.datetime.min.strftime("%y-%m-%d %H:%M:%S")
    if instance != None and instance.warning and instance.toRoute and warning == min_date:
        #print("--2--")
        #subject = Config.get_value("EMAIL_WARNING_SUBJECT").replace("__RES__", waste).replace("__INS__", facility)
        #html = Config.get_value("EMAIL_WARNING_HTML").replace("__RES__", waste).replace("__INS__", facility)
        email_to = instance.emails.split(",")
        send_warning_level_email(email_to, instance.subject, instance.body, instance.waste.name, instance.facility.description)
        instance.last_warning = datetime.datetime.now()
        #instance.save()
        if not hasattr(instance, '_guardar_recursivo'):
            instance._guardar_recursivo = True  # Bandera de control
            instance.save()
            delattr(instance, '_guardar_recursivo')
    elif instance != None and instance.toRoute and instance.filling_degree < instance.warning_filling_degree:
        instance.last_warning = datetime.datetime.min
        #instance.save()
        if not hasattr(instance, '_guardar_recursivo'):
            instance._guardar_recursivo = True  # Bandera de control
            instance.save()
            delattr(instance, '_guardar_recursivo')

class FacilityManteinanceConcept(models.Model):
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Concepto de mantenimiento'

class FacilityManteinanceStatus(models.Model):
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estado de mantenimiento'

class FacilityManteinance(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name=('Fecha'))
    end_date = models.DateTimeField(default=datetime.datetime.min, null=True, verbose_name=('Fecha de fin'))
    observations = models.TextField(verbose_name = _('Observaciones'), null=True, default='', blank=True)

    concept = models.ForeignKey(FacilityManteinanceConcept, verbose_name=_('Concepto'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")
    status = models.ForeignKey(FacilityManteinanceStatus, verbose_name=_('Estado'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")
    facility = models.ForeignKey(Facility, verbose_name=_('Instalación'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")

    class Meta:
        verbose_name = _('Mantenimiento en instalación')
        ordering = ['-date']

def upload_fac_man_image(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "facilities/manteinance/"
    return '/'.join([folder, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class FacilityManteinanceImage(models.Model):
    image = models.ImageField(upload_to=upload_fac_man_image, blank=True, verbose_name="Imagen", help_text="Select file to upload")
    fac_man = models.ForeignKey(FacilityManteinance, verbose_name=_('Mantenimiento'), on_delete=models.SET_NULL, null=True, blank=True, related_name="images")

    class Meta:
        verbose_name = _('Imágenes de mantenimiento')

class FacilityWasteManager(models.Model):
    waste = models.ForeignKey(Waste, verbose_name=_('Tratemiento'), on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(Company, verbose_name=_("Gestor Externo"), on_delete=models.SET_NULL, blank=True, null=True)
    facility = models.ForeignKey(Facility, verbose_name=_("Instalación"), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Gestor de Residuo'
        verbose_name_plural = 'Gestores de Residuos'


'''
    TRUCKS
'''
class TruckType(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    brand = models.CharField(max_length=90, verbose_name=_('Marca'), null=True)
    model = models.CharField(max_length=90, verbose_name=_('Modelo'), null=True)
    year = models.CharField(max_length=4, verbose_name=_('Año'), null=True)

    def __str__(self):
        return "%s %s (%s)" % (self.brand, self.model, self.year)

    class Meta:
        verbose_name=_('Tipo de camión')
        verbose_name_plural=_('Tipos de camión')

class Truck(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    #location = models.PointField(verbose_name = 'Localización', null=True)
    available = models.BooleanField(verbose_name=_('Disponible'), default=True)
    on_saturday = models.BooleanField(verbose_name=_('Disponible en Sábado'), default=False)
    itv_date = models.DateField(default=datetime.datetime.today, null=True, verbose_name=('Fecha de ITV'))
    number_plate = models.CharField(max_length=10, verbose_name = 'Matrícula')
    observations = models.TextField(verbose_name = _('Observaciones'), null=True, default='', blank=True)

    lat = models.CharField(max_length=50, verbose_name=_("Lat"), default="", null=True)
    lon = models.CharField(max_length=50, verbose_name=_("Lon"), default="", null=True)

    type = models.ForeignKey(TruckType, verbose_name='Tipo de Camión', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, verbose_name='Empresa', on_delete=models.SET_NULL, null=True)
    base_station = models.ForeignKey(Facility, verbose_name='Estación Base', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return ("[%s] - %s" % (self.number_plate.upper(), self.type))

    @property
    def name(self):
        #print( "{} {} ({})".format(self.type.brand, self.type.model, self.number_plate))
        if self != None:
            if self.type != None:
                return "{} {} ({})".format(self.type.brand, self.type.model, self.number_plate)
            else:
                return "{}".format(self.number_plate)
        return ""

    @property
    def current_driver(self):
        et = EmployeeTruck.objects.filter(truck=self).order_by("-date").first()
        return et.employee if et != None else None


    class Meta:
        verbose_name = 'Camión'
        verbose_name_plural = ('Camiones')
        #ordering = ['base_station', 'type', 'number_plate']

class TruckManteinanceConcept(models.Model):
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Concepto de mantenimiento camiones'

class TruckManteinanceStatus(models.Model):
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estado de mantenimiento del camión'

class TruckManteinance(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name=('Fecha'))
    end_date = models.DateTimeField(default=datetime.datetime.min, null=True, verbose_name=('Fecha de fin'))
    observations = models.TextField(verbose_name = _('Observaciones'), null=True, default='', blank=True)

    concept = models.ForeignKey(TruckManteinanceConcept, verbose_name=_('Concepto'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")
    status = models.ForeignKey(TruckManteinanceStatus, verbose_name=_('Estado'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")
    truck = models.ForeignKey(Truck, verbose_name=_('Camión'), on_delete=models.SET_NULL, null=True, blank=True, related_name="manteinances")

    class Meta:
        verbose_name = _('Mantenimiento camiones')
        ordering = ['-date']

def upload_truck_man_image(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "trucks/manteinance/"
    return '/'.join([folder, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class TruckManteinanceImage(models.Model):
    image = models.ImageField(upload_to=upload_fac_man_image, blank=True, verbose_name="Imagen", help_text="Select file to upload")
    truck_man = models.ForeignKey(TruckManteinance, verbose_name=_('Mantenimiento'), on_delete=models.SET_NULL, null=True, blank=True, related_name="images")

    class Meta:
        verbose_name = _('Imágenes de mantenimiento camiones')


'''
    EMPLOYEE
'''
class EmployeeType(models.Model):
    code = models.CharField(max_length=10, null=True, verbose_name=_('Código'))
    name = models.CharField(max_length=100, null=True, verbose_name=_('Nombre'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name=_('Tipo de empleado')
        verbose_name_plural=_('Tipos de Empleados')

class Employee(models.Model):
    ext_code = models.IntegerField(verbose_name=_('External code'), null=True, blank=True, default=0)
    active = models.BooleanField(default=True, verbose_name=_('Activo'), blank=True)
    code = models.CharField(max_length=10, null=True, verbose_name='Código de Empleado', default="")
    nif = models.CharField(max_length=10, null=True, verbose_name=_('NIF'), default="")
    pin = models.CharField(max_length=10, null=True, verbose_name=_('PIN'), default="")
    device_uid = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('DeviceUID'))
    name = models.CharField(max_length=100, null=True, verbose_name=_('Nombre'))
    surname = models.CharField(max_length=100, null=True, verbose_name=_('Apellidos'))
    cellphone = models.CharField(max_length=10, null=True, default = '0000000000', verbose_name = 'Teléfono de contacto')
    email = models.EmailField(null=True, verbose_name = _('Email de contacto'))

    user = models.OneToOneField(User, verbose_name='Usuario', on_delete=models.CASCADE, null=True, blank=True, related_name='employee')
    company = models.ForeignKey(Company, verbose_name='Empresa', on_delete=models.CASCADE, null=True, related_name="employees")
    facility = models.ForeignKey(Facility, verbose_name=_('Instalación'), on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
    rol = models.ForeignKey(EmployeeType, verbose_name=_('Tipo'), on_delete=models.SET_NULL, null=True, blank=True)

    #def __str__(self):
    #    return self.name

    @property
    def is_driver(self):
        return (self.rol != None and self.rol.code == "driver")

    @property
    def is_driver_mpl(self):
        return (self.rol != None and self.rol.code == "driver_mpl")

    @property
    def is_operator(self):
        return (self.rol != None and self.rol.code == "operator")

    @property
    def is_external(self):
        return (self.rol != None and self.rol.code == "external")

    @property
    def truck(self):
        et = self.trucks.order_by("-date").first()
        return et.truck if et != None else None

    @property
    def full_name(self):
        return "{} {}".format(self.name, self.surname)

    @property
    def current_km(self):
        now = datetime.datetime.now()
        idate = now.replace(hour=0, minute=0, second=0)
        edate = now.replace(hour=23, minute=59, second=59)
        return EmployeeTruckKm.objects.filter(employee=self, truck=self.truck, date__range=(idate, edate)).first()

    def generate_pin(self):
        mypin = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        while (Employee.objects.filter(pin = mypin).exists()):
            mypin = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.pin = mypin
        self.save()

    def save_user(self):
        if self.user == None:
            self.user = User.objects.create_user(username=self.email, email=self.email)
            self.user.first_name = self.name
            self.user.last_name = self.surname
            self.save()
            group = Group.objects.get(name='operators')
            group.user_set.add(self.user)
        else:
            self.user.username = self.email
            self.user.first_name = self.name
            self.user.last_name = self.surname
            self.user.save()

    @staticmethod
    def getOperators():
        return Employee.objects.filter(rol__code = "operator")

    @staticmethod
    def getOperatorsUser():
        return [item for item in Employee.objects.filter(rol__code = "operator")]

    @staticmethod
    def getOperatorsUserByFacility(fac_id):
        return [item for item in Employee.objects.filter(rol__code = "operator", facility__id=fac_id)]

    class Meta:
        verbose_name=_('Empleado')
        verbose_name_plural=_('Empleados')
        ordering = ['code','name']

class EmployeeTruck(models.Model):
    date = models.DateTimeField(verbose_name=('Fecha de ITV'), null=True, default=datetime.datetime.now)
    employee = models.ForeignKey(Employee, verbose_name='Empleado', on_delete=models.CASCADE, null=True, related_name="trucks")
    truck= models.ForeignKey(Truck, verbose_name='Vehículo', on_delete=models.SET_NULL, null=True, related_name="employees")

    class Meta:
        verbose_name=_('Empleado Camion')
        verbose_name_plural=_('Empleados Camiones')

class EmployeeAccessLog(models.Model):
    finish = models.BooleanField(default=False, verbose_name=_('Finalizada'));
    date = models.DateTimeField(verbose_name=('Fecha de acceso'), null=True, default=datetime.datetime.now)
    location = models.TextField(verbose_name=('Fecha de acceso'), null=True, default="")
    employee = models.ForeignKey(Employee, verbose_name='Empleado', on_delete=models.CASCADE, null=True, related_name="access")

    class Meta:
        verbose_name=_('Acceso de Empleado')
        verbose_name_plural=_('Acceso de Empleados')

class EmployeeTruckKm(models.Model):
    date = models.DateTimeField(verbose_name=('Fecha de ITV'), null=True, default=datetime.datetime.now)
    km = models.CharField(max_length=100, verbose_name='Km', default="")
    employee = models.ForeignKey(Employee, verbose_name='Empleado', on_delete=models.SET_NULL, null=True, related_name="trucks_km")
    truck= models.ForeignKey(Truck, verbose_name='Vehículo', on_delete=models.CASCADE, null=True, related_name="employees_km")

    class Meta:
        verbose_name=_('Empleado Camion Km')
        verbose_name_plural=_('Empleados Camiones Km')

'''
    Tray
'''
class Tray(models.Model):
    number = models.CharField(max_length=100, verbose_name='Número')

    def __str__(self):
        return self.number

    @property
    def current_location(self):
        track = self.tracking.all().order_by("-end_date").first()
        if track != None:
            return track.target.description if track.target != None else track.source.description
    @property
    def current_date(self):
        track = self.tracking.all().order_by("-end_date").first()
        if track != None:
            return track.end_date if track.finish else track.ini_date

    def last_tracking(self):
        return self.tracking.all().order_by("-end_date").first()

    def last_route(self):
        return self.routes.all().order_by("-end_date").first()

    class Meta:
        verbose_name=_('Bandeja')
        verbose_name_plural=_('Bandejas')

class TrayTracking(models.Model):
    finish = models.BooleanField(default=False, verbose_name=_('Finalizada'));
    ini_date = models.DateTimeField(verbose_name=('Inicio'), null=True, default=tz.now)
    end_date = models.DateTimeField(verbose_name=('Fin'), null=True, default=tz.now)

    source = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Origen', null=True, related_name="trays_source")
    target = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Destino', null=True, related_name="trays_target")
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, verbose_name='Camión', null=True)
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name=_('Conductor'), null=True)
    tray = models.ForeignKey(Tray, on_delete=models.CASCADE, verbose_name='Bandeja', null=True, related_name="tracking")

    @staticmethod
    def startTracking(driver, source, tray):
        return TrayTracking.objects.create(ini_date=tz.now(), source=source, truck=driver.truck, driver=driver, tray=tray)

    @staticmethod
    def finishTracking(driver, target):
        tt = TrayTracking.objects.filter(driver=driver, finish=False).first()
        if tt != None:
            tt.target = target
            tt.end_date = tz.now()
            tt.finish = True
            tt.save()

    class Meta:
        verbose_name=_('Localización Bandeja')
        verbose_name_plural=_('Localización Bandejas')

'''
    ROUTES
'''
def upload_route_image(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "routes/%s" % (instance.id)
    return '/'.join([folder, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class Route(models.Model):
    finish = models.BooleanField(default=False, verbose_name=_('Finalizada'));
    weight = models.FloatField(default=0, verbose_name= _('Peso'))
    code = models.CharField(max_length=8, verbose_name='Código')
    ini_date = models.DateTimeField(verbose_name=('Inicio'), null=True, default=tz.now)
    end_date = models.DateTimeField(verbose_name=('Fin'), null=True, default=tz.now)
    image = models.ImageField(upload_to=upload_route_image, blank=True, verbose_name="Imagen", help_text="Select file to upload")

    source = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Origen', null=True, related_name="routes_source")
    target = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Destino', null=True, related_name="routes_target")
    waste = models.ForeignKey(WasteInFacility, on_delete=models.SET_NULL, verbose_name='Residuo', null=True)
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, verbose_name='Camión', null=True)
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name=_('Conductor'), null=True)
    tray = models.ForeignKey(Tray, on_delete=models.SET_NULL, verbose_name='Bandeja', null=True, related_name="routes")
    #company = models.ForeignKey(Company, on_delete=models.SET_NULL, verbose_name=_('Company'), null=True, blank=True, default=None)

    @property
    def ref(self):
        return "3500000514{}{}".format(self.ini_date.year, str(self.pk).zfill(7))

    def jsonDoc(self):
        return route_to_json(self)

    def source_by_tray(self):
        route = Route.objects.filter(tray=self.tray).order_by("-end_date").exclude(id=self.id).first()
        return route.source.description if route != None and route.source != None else ""

    @staticmethod
    def getCurrent(driver):
        return Route.objects.filter(driver=driver, finish=False).first()

    class Meta:
        verbose_name=_('Ruta')
        verbose_name_plural=_('Rutas')
        ordering=['-ini_date']

class RouteMpl(models.Model):
    finish = models.BooleanField(default=False, verbose_name=_('Finalizada'));
    code = models.CharField(max_length=8, verbose_name='Código')
    ini_date = models.DateTimeField(verbose_name=('Inicio'), null=True, default=tz.now)
    end_date = models.DateTimeField(verbose_name=('Fin'), null=True, default=tz.now)

    #source = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Origen', null=True, related_name="routes_mpl_source")
    target = models.ForeignKey(Facility,on_delete=models.SET_NULL, verbose_name='Destino', null=True, related_name="routes_mpl_target")
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, verbose_name='Camión', null=True)
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name=_('Conductor'), null=True)

    @staticmethod
    def currentRoute(driver):
        route = RouteMpl.objects.filter(driver=driver, truck=driver.truck, finish=False).first()
        return route if route != None else RouteMpl.objects.create(driver=driver, truck=driver.truck, code="MPL")

    class Meta:
        verbose_name=_('Ruta MPL')
        verbose_name_plural=_('Rutas MPL')
        ordering=['-ini_date']

class RouteMplPoint(models.Model):
    weight = models.FloatField(default=0, verbose_name= _('Peso'))
    date = models.DateTimeField(verbose_name=('Fecha'), null=True, default=tz.now)

    mpl = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Origen', null=True, related_name="routes_mpl")
    waste = models.ForeignKey(WasteInFacility, on_delete=models.SET_NULL, verbose_name='Residuo', null=True)
    route = models.ForeignKey(RouteMpl, on_delete=models.CASCADE, verbose_name='Ruta', null=True, related_name="points")

    class Meta:
        verbose_name=_('Punto de Ruta MPL')
        verbose_name_plural=_('Puntos de Rutas MPL')
        ordering=['-date']

class RouteExt(models.Model):
    weight = models.FloatField(default=0, verbose_name= _('Peso'))
    date = models.DateTimeField(verbose_name=('Fecha'), null=True, default=tz.now)
    get_date = models.DateTimeField(verbose_name=('Fecha de recogida'), null=True, default=tz.now)

    waste = models.ForeignKey(WasteInFacility, on_delete=models.SET_NULL, verbose_name='Residuo', null=True)
    facility = models.ForeignKey(Facility,on_delete=models.SET_NULL,verbose_name='Destino',null=True,related_name="routes_ext")
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name=_('Conductor'), null=True)
    external_manager = models.ForeignKey(Company, verbose_name=_("Gestor Externo"), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name=_('Ruta Externa')
        verbose_name_plural=_('Rutas Externas')
        ordering=['-date']


'''
    Facility Actions
'''
class FacilityActionType(models.Model):
    code = models.CharField(max_length=8, verbose_name='Código')
    name = models.CharField(max_length=255, verbose_name='Nombre')

    class Meta:
        verbose_name=_('Otra acción')
        verbose_name_plural=_('Otras acciones')


class FacilityActions(models.Model):
    date = models.DateTimeField(verbose_name=('Inicio'), null=True, default=tz.now)

    fa_type = models.ForeignKey(FacilityActionType, on_delete=models.SET_NULL, verbose_name='Tipo', null=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, verbose_name='Origen', null=True, related_name="actions")
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, verbose_name='Camión', null=True)
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name=_('Conductor'), null=True, related_name="actions")

    class Meta:
        verbose_name=_('Otra acción conductor')
        verbose_name_plural=_('Otras acciones conductores')
        ordering=['-date']

'''
    Items
'''
class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre', default="")
    amount = models.IntegerField(verbose_name='Cantidad', default=0)

    def __str__(self):
        return self.name

    def add_amount(self, amount):
        self.amount += amount
        self.save()
        return self.amount

    def sub_amount(self, amount):
        self.amount -= amount
        self.save()
        return self.amount

    class Meta:
        verbose_name=_('Material')
        verbose_name_plural=_('Materiales')
        ordering = ["name"]

class EmployeeItem(models.Model):
    returned = models.BooleanField(default = False, verbose_name=_('Devuelto'));
    date = models.DateTimeField(verbose_name=('Fecha de prestamo'), null=True, default=datetime.datetime.now)
    return_date = models.DateTimeField(verbose_name=('Fecha de devolución'), null=True, default=datetime.datetime.now)
    #action = models.CharField(max_length=255, verbose_name='Acción', default="")
    amount = models.IntegerField(verbose_name='Cantidad', default=0)
    desc = models.TextField(verbose_name='Descripción', default="")
    employee = models.ForeignKey(Employee, verbose_name='Empleado', on_delete=models.CASCADE, null=True, related_name="items")
    item = models.ForeignKey(Item, verbose_name='Material', on_delete=models.SET_NULL, null=True, related_name="employees")

    class Meta:
        verbose_name=_('Empleado Material')
        verbose_name_plural=_('Empleados Materiales')

class FacilityItem(models.Model):
    returned = models.BooleanField(default = False, verbose_name=_('Devuelto'));
    date = models.DateTimeField(verbose_name=('Fecha de prestamo'), null=True, default=datetime.datetime.now)
    return_date = models.DateTimeField(verbose_name=('Fecha de devolución'), null=True, default=datetime.datetime.now)
    amount = models.IntegerField(verbose_name='Cantidad', default=0)
    desc = models.TextField(verbose_name='Descripción', default="")
    facility = models.ForeignKey(Facility, verbose_name='Instalación', on_delete=models.CASCADE, null=True, related_name="items")
    item = models.ForeignKey(Item, verbose_name='Material', on_delete=models.SET_NULL, null=True, related_name="facilities")

    class Meta:
        verbose_name=_('Instalación Material')
        verbose_name_plural=_('Instalaciones Materiales')

'''
    Contract
'''
class AgreementType(models.Model):
    code = models.CharField(max_length=20, verbose_name='Código', default="")
    name = models.CharField(max_length=255, verbose_name='Nombre', default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name=_('Tipo de convenio')
        verbose_name_plural=_('Tipos de convenio')

class ContractType(models.Model):
    code = models.CharField(max_length=20, verbose_name='Código', default="")
    name = models.CharField(max_length=255, verbose_name='Nombre', default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name=_('Tipo de contrato')
        verbose_name_plural=_('Tipos de contrato')

class EmployeeContract(models.Model):
    ini_date = models.DateTimeField(verbose_name=('Fecha de inicio'), null=True, default=datetime.datetime.now)
    end_date = models.DateTimeField(verbose_name=('Fecha de fin'), null=True, default=datetime.datetime.now)
    timetable = models.TextField(verbose_name='Horario', default="")

    employee = models.ForeignKey(Employee, verbose_name='Empleado', on_delete=models.CASCADE, null=True, related_name="contracts")
    contract_type = models.ForeignKey(ContractType, verbose_name='Tipo de contrato', on_delete=models.SET_NULL, null=True, related_name="employees")
    agreement_type = models.ForeignKey(AgreementType, verbose_name='Tipo de convenio', on_delete=models.SET_NULL, null=True, related_name="employees")

    class Meta:
        verbose_name=_('Empleado Material')
        verbose_name_plural=_('Empleados Materiales')

