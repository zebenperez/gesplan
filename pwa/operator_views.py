from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt

from gesplan.decorators import group_required_pwa
from gesplan.commons import get_or_none, get_param, show_exc, get_float
from gestion.models import EmployeeTruck, Truck, Facility, Waste, WasteInFacility, Route, FacilityActions, FacilityActionType
from gestion.models import Tray, TrayTracking, RouteExt
from incidents.models import Incident, IncidentType
from citizens.models import Citizen, Town, WasteCitizen

import random, string


'''
    OPERATOR
'''
@group_required_pwa("operators")
def operator_home(request):
    try:
        return redirect(reverse("pwa-operator-wastes"))
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

'''
    WASTES
'''
@group_required_pwa("operators")
def operator_wastes(request):
    item_list = WasteInFacility.objects.filter(facility=request.user.employee.facility)
    return render(request, "operator/wastes.html", {'item_list': item_list, 'now': datetime.now()})

@group_required_pwa("operators")
def operator_wastes_form(request):
    obj = get_or_none(WasteInFacility, get_param(request.GET, "obj_id"))
    return render(request, "operator/wastes-form.html", {'obj': obj,})

@group_required_pwa("operators")
def operator_wastes_save(request):
    try:
        obj = get_or_none(WasteInFacility, get_param(request.POST, "obj_id"))
        #val = get_float(get_param(request.GET, "value"))
        val = get_float(get_param(request.POST, "filling_degree"))
        re = RouteExt.objects.filter(waste=obj, weight=0).first()
        #if obj.filling_degree > 0 and val == 0 and not obj.toRoute and obj.waste.external_manager != None:
        #if val >= obj.warning_filling_degree and not obj.toRoute and obj.waste.external_manager != None and re == None:
        #    RouteExt.objects.create(waste=obj, facility=obj.facility, external_manager=obj.waste.external_manager)
        manager = obj.external_manager
        if val >= obj.warning_filling_degree and not obj.toRoute and manager != None and re == None:
            RouteExt.objects.create(waste=obj, facility=obj.facility, external_manager=manager)
        obj.show_user = True if get_param(request.POST, "show_user") != "" else False
        obj.filling_degree = val
        obj.save()
        return redirect("pwa-operator")
        #return HttpResponse("Saved!")
    except Exception as e:
        print(e)
        return HttpResponse(e)

'''
    CITIZENS
'''
@group_required_pwa("operators")
def operator_citizens(request):
    # Is summer time in effect?


    now = datetime.now()
    is_monday = datetime.today().weekday() == 0
    is_saturday = datetime.today().weekday() == 5
    start_shift = now.replace(hour=00, minute=1)
    end_shift = now.replace(hour=13, minute=59)
    if is_monday:
        end_shift = now.replace(hour=16, minute=29)
    elif is_saturday:
        end_shift = now.replace(hour=14, minute=29)
    if (now > end_shift):
        start_shift = start_shift.replace(hour=14, minute=00)
        if is_monday:
            start_shift=start_shift.replace(hour=16, minute=30)
        elif is_saturday:
            start_shift=start_shift.replace(hour=14, minute=30)
        end_shift = end_shift.replace(hour=23, minute=59)

    # Cambio horario
    from pytz import timezone
    from datetime import timedelta
    tz = timezone('Atlantic/Canary')
    if tz.dst(datetime.now()) != timedelta(0):
        offset = 1
    else:
        offset = 0

    end_shift -= timedelta(hours=offset)
    start_shift -= timedelta(hours=offset)
    # Fin cambio horario

    fac = request.user.employee.facility
    citizen_list = Citizen.objects.filter(facility=fac, date__gte=start_shift, date__lte=end_shift).order_by('-pk')
    #print(citizen_list)
    return render(request, "operator/citizens.html", {'citizen_list': citizen_list, 'today': now})

@group_required_pwa("operators")
def operator_citizens_form(request):
    emp = request.user.employee
    obj = get_or_none(Citizen, get_param(request.GET, "obj_id"))
    #obj = obj if obj != None and obj != "" else Citizen.objects.create(employee=emp, facility=emp.facility)
    return render(request, "operator/citizens-form.html", {'obj': obj, 'town_list': Town.objects.all()})

@group_required_pwa("operators")
def operator_citizens_save(request):
    emp = request.user.employee
    obj = get_or_none(Citizen, get_param(request.POST, "obj_id"))
    if obj == None:
        obj = Citizen.objects.create(employee=emp, facility=emp.facility)
    obj.town = get_or_none(Town, get_param(request.POST, "town"))
    obj.identification = get_param(request.POST, "identification")
    obj.phone = get_param(request.POST, "phone")
    obj.email = get_param(request.POST, "email")
    obj.plate = get_param(request.POST, "plate")
    obj.address = get_param(request.POST, "address")
    obj.observations = get_param(request.POST, "observations")
    obj.save()
    return render(request, "operator/citizens-waste-form.html", {'obj': obj, 'waste_list': Waste.objects.all()})
    #return redirect(reverse("pwa-operator-citizens"))

@group_required_pwa("operators")
def operator_citizens_waste_save(request):
    obj = get_or_none(Citizen, get_param(request.POST, "obj_id"))
    waste = get_or_none(Waste, get_param(request.POST, "waste"))
    units = get_float(get_param(request.POST, "units"))
    total = obj.total_by_waste(waste)
    if (total + units) > waste.day_limit:
        msg = "Se ha superado el límite diario!"
        context = {'obj': obj, 'waste_list': Waste.objects.all(), 'waste_id': waste.id, 'units': units, 'msg': msg}
        return render(request, "operator/citizens-waste-form.html", context)

    WasteCitizen.objects.create(citizen=obj, waste=waste, units=units)
    return render(request, "operator/citizens-waste-form.html", {'obj': obj, 'waste_list': Waste.objects.all()})

@group_required_pwa("operators")
def operator_citizens_waste_force(request):
    obj = get_or_none(Citizen, get_param(request.GET, "obj_id"))
    waste = get_or_none(Waste, get_param(request.GET, "waste"))
    units = get_float(get_param(request.GET, "units"))
    WasteCitizen.objects.create(citizen=obj, waste=waste, units=units)
    return render(request, "operator/citizens-waste-form.html", {'obj': obj, 'waste_list': Waste.objects.all()})

@group_required_pwa("operators")
def operator_citizens_remove(request, obj_id):
    obj = get_or_none(Citizen, obj_id)
    if obj != None:
        obj.delete()
    return redirect(reverse("pwa-operator-citizens"))

@group_required_pwa("operators")
def operator_citizens_waste_remove(request):
    obj = get_or_none(WasteCitizen, get_param(request.GET, "obj_id"))
    citizen = obj.citizen
    if obj != None:
        obj.delete()
    return render(request, "operator/citizens-waste-form.html", {'obj': citizen, 'waste_list': Waste.objects.all()})


'''
    FACILITIES
'''
@group_required_pwa("operators")
def facility_select(request):
    return render(request, "operator/facility-select.html", {'fac_list': Facility.getPL()})

@group_required_pwa("operators")
def facility_save(request):
    try:
        fac = get_or_none(Facility, get_param(request.POST, "facility"))
        if fac != None:
            #Asignamos la instalación al operador
            emp = request.user.employee
            emp.facility = fac
            emp.save()
            return redirect(reverse('pwa-operator'))
        else:
            return (render(request, "error_exception.html", {'exc': 'Instalación no encontrada!'}))
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))
    



