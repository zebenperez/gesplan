from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from datetime import datetime

from gesplan.decorators import group_required_pwa
from gesplan.commons import get_or_none, get_param, show_exc
from gestion.models import EmployeeTruck, Truck, Facility, Waste, WasteInFacility, Route, FacilityActions, FacilityActionType
from gestion.models import Tray, TrayTracking
from incidents.models import Incident, IncidentType

import random, string


'''
    DRIVERS
'''
@group_required_pwa("drivers")
def driver_home(request):
    try:
        if request.user.employee.truck == None:
            return redirect(reverse("pwa-select-truck"))
            #return redirect(reverse("pwa-driver-select-truck"))
        if request.user.employee.current_km == None:
            return redirect(reverse("pwa-set-km"))
        return redirect(reverse("pwa-driver-routes"))
        #return render(request, "drivers/home.html", {"now": datetime.now()})
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

'''
    ROUTES
'''
@group_required_pwa("drivers")
def driver_routes(request):
    #route = Route.objects.filter(finish=False).first()
    route = Route.getCurrent(request.user.employee)
    now = datetime.now()
    idate = now.replace(hour=0, minute=0)
    edate = now.replace(hour=23, minute=59)
    item_list = Route.objects.filter(driver=request.user.employee, finish=True, ini_date__range=(idate, edate))
    action_list = FacilityActions.objects.filter(driver=request.user.employee, date__range=(idate, edate))
    return render(request, "drivers/routes.html", {'route': route, 'item_list': item_list, 'action_list': action_list, 'now': now})

@group_required_pwa("drivers")
def driver_routes_source(request):
    #item_list = Facility.objects.filter(description__icontains="Punto")
    #return render(request, "drivers/routes-source.html", {'item_list': item_list})
    context = {'truck': request.user.employee.truck, "item_list": Facility.getPL(), 'tray_list': Tray.objects.all()}
    return render(request, "drivers/routes-source.html", context)

@group_required_pwa("drivers")
def driver_routes_waste(request):
    source = get_or_none(Facility, get_param(request.GET, "value"))
    tray = get_or_none(Tray, get_param(request.GET, "tray"))
    TrayTracking.finishTracking(request.user.employee, source)
    TrayTracking.startTracking(request.user.employee, source, tray)
    #item_list = Waste.objects.all()
    return render(request, "drivers/routes-waste.html", {'item_list':source.waste_by_filling_degree(), 'source':source, 'tray':tray})

@group_required_pwa("drivers")
def driver_routes_confirm(request):
    source = get_or_none(Facility, get_param(request.GET, "source"))
    tray = get_or_none(Tray, get_param(request.GET, "tray"))
    waste = get_or_none(WasteInFacility, get_param(request.GET, "value"))
    return render(request, "drivers/routes-confirm.html", {'waste': waste, 'source': source, 'tray': tray})

@group_required_pwa("drivers")
def driver_routes_start(request, source, waste, tray):
    try:
        s = get_or_none(Facility, source)
        t = get_or_none(Tray, tray)
        w = get_or_none(WasteInFacility, waste)
        Route.objects.create(source=s, waste=w, truck=request.user.employee.truck, driver=request.user.employee, tray=t, code="PL")
        return redirect("pwa-driver-routes")
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("drivers")
def driver_routes_target(request, route):
    r = get_or_none(Route, route)
    #item_list = Facility.objects.filter(description__icontains="Punto")
    return render(request, "drivers/routes-target.html", {'route': r, 'item_list': Facility.getTargets()})

@group_required_pwa("drivers")
def driver_routes_finish(request):
    route = get_or_none(Route, get_param(request.POST, "route"))
    target = get_or_none(Facility, get_param(request.POST, "target"))
    weight = get_param(request.POST, "weight")
    if "file" in request.FILES:
        image = request.FILES["file"] 
        route.image = image
    if "file2" in request.FILES:
        image = request.FILES["file2"] 
        route.image = image
    route.target = target
    route.target = target
    route.weight = weight
    route.end_date = datetime.now()
    route.finish = True
    route.save()
    return redirect(reverse("pwa-driver-routes"))
    #return render(request, "drivers/routes-finish.html", {'route': route})
    #return render(request, "drivers/routes-finish.html", {'route': route, 'target': target, 'weight': weight})

@group_required_pwa("drivers")
def driver_routes_dir(request, route_id):
    route = get_or_none(Route, route_id)
    return render(request, "drivers/driver-doc.html", {'route': route, 'datas': route.jsonDoc()})


@group_required_pwa("drivers")
def driver_routes_source_exp(request):
    tray_list = []
    for tray in Tray.objects.all():
        track = tray.last_tracking()
        if track != None and track.target !=None and track.target.code == "EXP":
            tray_list.append(tray)
    context = {'truck': request.user.employee.truck, 'tray_list': tray_list}
    return render(request, "drivers/routes-source-exp.html", context)

@group_required_pwa("drivers")
def driver_routes_start_exp(request):
    try:
        tray = get_or_none(Tray, get_param(request.POST, "tray"))
        source = get_or_none(Facility, "EXP", "code")
        tt = TrayTracking.startTracking(request.user.employee, source, tray)
        last_route = tray.last_route()
        emp = request.user.employee
        route = Route.objects.create(source=source, waste=last_route.waste, truck=emp.truck, driver=emp, tray=tray, code="PL")
        return redirect("pwa-driver-routes")
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("drivers")
def driver_routes_target_exp(request, route):
    r = get_or_none(Route, route)
    target = get_or_none(Facility, "EXP", "code")

    TrayTracking.finishTracking(request.user.employee, target)

    r.target = target
    r.end_date = datetime.now()
    r.finish = True
    r.save()
    return redirect(reverse("pwa-driver-routes"))


#'''
#    ACTIONS
#'''
#@group_required_pwa("drivers")
#def actions(request):
#    #now = datetime.now()
#    #idate = now.replace(hour=0, minutes=0)
#    #edate = now.replace(hour=23, minutes=59)
#    fac_list = Facility.getPL()
#    action_list = FacilityActionType.objects.all()
#    #fa_list = FacilityActions.objects.filter(driver=request.user.driver, date__range=(idate, edate))
#    return render(request, "drivers/actions.html", {'action_list': action_list, 'fac_list': fac_list})
#
#@group_required_pwa("drivers", "drivers_mpl")
#def save_action(request):
#    try:
#        fac = get_or_none(Facility, get_param(request.POST, "facility"))
#        action = get_or_none(FacilityActionType, get_param(request.POST, "action"))
#        if fac != "" and action != "":
#            emp = request.user.employee
#            fa = FacilityActions.objects.create(facility=fac, fa_type=action, driver=emp, truck=emp.truck)
#            return redirect("pwa-home")
#        else:
#            return (render(request, "error_exception.html", {'exc': 'Facility or Action not found!'}))
#    except Exception as e:
#        return (render(request, "error_exception.html", {'exc':show_exc(e)}))
#
#'''
#    INCIDENTS
#'''
#@group_required_pwa("drivers")
#def driver_incidents(request):
#    now = datetime.now()
#    idate = now.replace(hour=0, minute=0)
#    edate = now.replace(hour=23, minute=59)
#    item_list = Incident.objects.filter(owner=request.user, creation_date__range=(idate, edate))
#    return render(request, "drivers/incidents.html", {'item_list': item_list})
#
#@group_required_pwa("drivers")
#def driver_incidents_add(request):
#    return render(request, "drivers/incidents-form.html", {"type_list": IncidentType.objects.filter(driver=True)})
#
#@group_required_pwa("drivers")
#def driver_incidents_save(request):
#    try:
#        code =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
#        subject = get_param(request.POST, "subject")
#        description = get_param(request.POST, "description")
#        itype = get_or_none(IncidentType, get_param(request.POST, "type"))
#        Incident.objects.create(code=code, subject=subject, description=description, owner=request.user, type=itype)
#        return redirect("pwa-driver-incidents")
#    except Exception as e:
#        return (render(request, "error_exception.html", {'exc':show_exc(e)}))
#
#
