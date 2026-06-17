from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime

from gesplan.decorators import group_required
from gesplan.commons import get_float, get_or_none, get_param, get_session, set_session, show_exc
from incidents.models import Incident
from .models import Facility, FacilityWasteManager, FacilityActions
from .models import Route, RouteExt, Waste, WasteInFacility, Company, Employee, Truck, Tray
from .views import get_facilities


@group_required("admins",)
def index(request):
    #facilities = Facility.objects.filter(description__contains="Punto")
    #facilities_mpl = Facility.objects.filter(code__startswith="MPL-")
    facilities = Facility.getPL()
    facilities_mpl = Facility.getMPL()
    routes = get_routes(request)
    routes_mpl = get_routes(request, "MPL")
    routes_ext = RouteExt.objects.all()
    actions = FacilityActions.objects.all()
    incidents = Incident.objects.filter(closed=False)
    context = {
        "facilities":facilities,
        "facilities_mpl":facilities_mpl,
        "routes":routes,
        "routes_mpl":routes_mpl,
        "routes_ext":routes_ext,
        "incidents":incidents,
        "actions":actions
    }
    return render(request, "operations/index.html", context)

@group_required("admins",)
def facility_waste(request):
    fac = get_or_none(Facility, get_param(request.GET, "obj_id"))
    r = True if get_param(request.GET, "route") == "True" else False
    return render(request, "operations/facility-waste.html", {"item_list": fac.waste.filter(toRoute=r),})

@group_required("admins",)
def incidents_list(request):
    val = get_param(request.GET, "value")
    closed = True if val == "True" else False
    incidents = Incident.objects.filter(closed=closed)
    return render(request, "operations/incidents-list.html", {"incidents": incidents,})

'''
    ROUTES
'''
def get_routes(request, code="PL"):
    search_value = get_session(request, "s-truck-name")
    filters_to_search = ["name__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Route.objects.filter(full_query).filter(code=code)[:30]

@group_required("admins",)
def routes_view(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Route, obj_id)
    if obj == None:
        obj = Route.objects.create()
    return render(request, "operations/routes/routes-view.html", {'obj': obj})

@group_required("admins",)
def routes_list(request):
    return render(request, "operations/routes/routes-list.html", {"items": get_routes(request)})

@group_required("admins",)
def routes_ext_list(request):
    return render(request, "operations/routes/routes-list.html", {"items": RouteExt.objects.all()})

@group_required("admins",)
def routes_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Route, obj_id)
    if obj == None:
        obj = Route.objects.create()
    facs = Facility.getPL()
    wastes = WasteInFacility.objects.filter(facility=obj.source)
    trucks = Truck.objects.all()
    trays = Tray.objects.all()
    emps = Employee.objects.filter(rol__code="driver")
    context = {'obj': obj, 'fac_list': facs, 'waste_list': wastes, 'truck_list': trucks, 'tray_list': trays, 'emp_list': emps}
    return render(request, "operations/routes/routes-form.html", context)

@group_required("admins",)
def routes_source_save(request):
    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
    fac = get_or_none(Facility, get_param(request.GET, "value"))
    waste_list = WasteInFacility.objects.filter(facility=fac)
    obj.source = fac
    obj.save()
    return render(request, "operations/routes/routes-form-waste.html", {'obj': obj, 'waste_list': waste_list})


@group_required("admins",)
def routes_ext_form(request):
    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
    #if obj == None:
    #    obj = RouteExt.objects.create()
    return render(request, "operations/routes/routes-ext-form.html", {'obj': obj})

@group_required("admins",)
def routes_remove(request):
    obj = get_or_none(Route, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.delete()
    return render(request, "operations/routes/routes-list.html", {"items": get_routes(request)})

@group_required("admins",)
def routes_img_upload(request):
    route = get_or_none(Route, get_param(request.POST, "obj_id"))
    if route != None:
        route.image = request.FILES["file"]
        route.save()
    return render(request, "operations/routes/routes-form-image.html", {"obj": route})

@group_required("admins",)
def routes_img_remove(request):
    obj = get_or_none(Route, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.image.delete(save=True)
        obj.delete()
    return render(request, "operations/routes/routes-form-image.html", {"obj": obj})


'''
    OPERATIONS REPORTS
'''
def get_operation_report(request):
    #idate_ini = datetime.strptime(get_session(request, "sr_operation_idate_ini"), "%Y-%m-%d")
    #idate_ini = get_session(request, "sr_operation_idate_ini")
    #idate_end = get_session(request, "sr_operation_idate_end")
    edate_ini = get_session(request, "sr_operation_edate_ini")
    edate_end = get_session(request, "sr_operation_edate_end")
    waste = get_session(request, "sr_operation_waste")
    comp = get_session(request, "sr_operation_comp")
    fac = get_session(request, "sr_operation_fac")
    target = get_session(request, "sr_operation_target")
    plate = get_session(request, "sr_operation_plate")

    kwargs = {"code": "PL"}
    #if idate_ini != "":
    #    kwargs["ini_date__gte"] = idate_ini
    #if idate_end != "":
    #    kwargs["ini_date__lte"] = idate_end
    if edate_ini != "":
        kwargs["end_date__gte"] = edate_ini
    if edate_end != "":
        kwargs["end_date__lte"] = edate_end
    if waste != "":
        kwargs["waste__waste__id"] = waste
    if comp != "":
        kwargs["driver__company__id"] = comp
    if fac != "":
        kwargs["source__id"] = fac
    if target != "":
        kwargs["target__id"] = target
    if plate != "":
        kwargs["truck__number_plate__icontains"] = plate
    #print(kwargs)
    return Route.objects.filter(**kwargs).exclude(target__code = "EXP")

@group_required("admins",)
def report(request):
    context = {"items":[], "waste_list":Waste.objects.all(), "comp_list":Company.objects.all(), "fac_list":Facility.getPL(),}
    return render(request, "operations/reports/operations.html", context)

@group_required("admins",)
def report_search(request):
    #set_session(request, "sr_operation_idate_ini", get_param(request.GET, "sr_operation_idate_ini"))
    #set_session(request, "sr_operation_idate_end", get_param(request.GET, "sr_operation_idate_end"))
    set_session(request, "sr_operation_edate_ini", get_param(request.GET, "sr_operation_edate_ini"))
    set_session(request, "sr_operation_edate_end", get_param(request.GET, "sr_operation_edate_end"))
    set_session(request, "sr_operation_waste", get_param(request.GET, "sr_operation_waste"))
    set_session(request, "sr_operation_comp", get_param(request.GET, "sr_operation_comp"))
    set_session(request, "sr_operation_fac", get_param(request.GET, "sr_operation_fac"))
    set_session(request, "sr_operation_target", get_param(request.GET, "sr_operation_target"))
    set_session(request, "sr_operation_plate", get_param(request.GET, "sr_operation_plate"))
    return render(request, "operations/reports/operations-list.html", {"items": get_operation_report(request)})

@group_required("admins",)
def report_dir(request, route_id):
    route = get_or_none(Route, route_id)
    return render(request, "operations/reports/driver-doc.html", {'route': route, 'datas': route.jsonDoc()})

'''
    Externals
'''
def get_wastes_in_facility(facility, comp):
    waste_list = []
    w_list = WasteInFacility.objects.filter(facility=facility)
    for waste in w_list:
        if waste.external_manager == comp:
            waste_list.append(waste)
    return waste_list

@group_required("external",)
def index_external(request):
    items = RouteExt.objects.filter(external_manager=request.user.employee.company)
    routes = Route.objects.filter(driver__company=request.user.employee.company)
    return render(request, "operations/external/index.html", {"routes_ext": items, 'routes': routes})

@group_required("external",)
def routes_external_list(request):
    items = RouteExt.objects.filter(external_manager=request.user.employee.company)
    routes = Route.objects.filter(driver__company=request.user.employee.company)
    return render(request, "operations/external/routes-ext-list.html", {"routes_ext": items, 'routes': routes})

@group_required("external",)
def routes_external_form(request):
    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
    comp = request.user.employee.company
    if obj == None:
        obj = RouteExt.objects.create(external_manager=comp)
    fac_list = Facility.objects.filter(company=comp)
    emp_list = Employee.objects.filter(company=comp)
    #waste_list = Waste.objects.filter(external_manager=comp)
    #waste_list = WasteInFacility.objects.filter(facility=obj.facility, waste__external_manager=comp)
    waste_list = get_wastes_in_facility(obj.facility, comp)
    context = {'obj': obj, 'fac_list': fac_list, 'emp_list': emp_list, 'waste_list': waste_list}
    return render(request, "operations/external/routes-ext-form.html", context)

@group_required("external",)
def routes_external_facility_save(request):
    comp = request.user.employee.company
    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
    fac = get_or_none(Facility, get_param(request.GET, "value"))
    #waste_list = WasteInFacility.objects.filter(facility=fac, waste__external_manager=comp)
    waste_list = get_wastes_in_facility(fac, comp)
    obj.facility = fac
    obj.save()
    return render(request, "operations/external/routes-ext-form-waste.html", {'obj': obj, 'waste_list': waste_list})

@group_required("external",)
def routes_external_remove(request):
    obj = get_or_none(RouteExt, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.delete()
    items = RouteExt.objects.filter(external_manager=request.user.employee.company)
    routes = Route.objects.filter(driver__company=request.user.employee.company)
    return render(request, "operations/external/routes-ext-list.html", {"routes_ext": items, 'routes': routes})

@group_required("external",)
def facility_external(request):
    return render(request, "operations/external/facilities.html", {"facilities": request.user.employee.company.get_facilities()})

@group_required("external",)
def facility_waste_external(request):
    fac = get_or_none(Facility, get_param(request.GET, "obj_id"))
    route = True if get_param(request.GET, "route") == "True" else False
    return render(request, "operations/external/facility-waste.html", {"item_list": fac.waste.filter(toRoute=route),})

'''
    Cabildo
'''
@group_required("cabildo",)
def index_cabildo(request):
    facilities = Facility.getPL()
    facilities_mpl = Facility.getMPL()
    routes = get_routes(request)
    routes_mpl = get_routes(request, "MPL")
    routes_ext = RouteExt.objects.all()
    context = {"facilities":facilities,"facilities_mpl":facilities_mpl,"routes":routes,"routes_mpl":routes_mpl,"routes_ext":routes_ext}
    return render(request, "operations/cabildo/index.html", context)

@group_required("cabildo",)
def facility_waste_cabildo(request):
    fac = get_or_none(Facility, get_param(request.GET, "obj_id"))
    return render(request, "operations/cabildo/facility-waste.html", {"item_list": fac.waste.filter(toRoute=False),})

@group_required("cabildo",)
def routes_view_cabildo(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Route, obj_id)
    if obj == None:
        obj = Route.objects.create()
    return render(request, "operations/cabildo/routes-view.html", {'obj': obj})


#@group_required("external",)
#def routes_external_list(request):
#    items = RouteExt.objects.filter(external_manager=request.user.employee.company)
#    return render(request, "operations/external/routes-list.html", {"routes_ext": items})
#
#@group_required("external",)
#def routes_external_form(request):
#    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
#    comp = request.user.employee.company
#    if obj == None:
#        obj = RouteExt.objects.create(external_manager=comp)
#    fac_list = Facility.objects.filter(company=comp)
#    emp_list = Employee.objects.filter(company=comp)
#    #waste_list = Waste.objects.filter(external_manager=comp)
#    #waste_list = WasteInFacility.objects.filter(facility=obj.facility, waste__external_manager=comp)
#    waste_list = get_wastes_in_facility(obj.facility, comp)
#    context = {'obj': obj, 'fac_list': fac_list, 'emp_list': emp_list, 'waste_list': waste_list}
#    return render(request, "operations/external/routes-ext-form.html", context)
#
#@group_required("external",)
#def routes_external_facility_save(request):
#    comp = request.user.employee.company
#    obj = get_or_none(RouteExt, get_param(request.GET, "obj_id"))
#    fac = get_or_none(Facility, get_param(request.GET, "value"))
#    #waste_list = WasteInFacility.objects.filter(facility=fac, waste__external_manager=comp)
#    waste_list = get_wastes_in_facility(fac, comp)
#    obj.facility = fac
#    obj.save()
#    return render(request, "operations/external/routes-ext-form-waste.html", {'obj': obj, 'waste_list': waste_list})
#
#@group_required("external",)
#def routes_external_remove(request):
#    obj = get_or_none(RouteExt, request.GET["obj_id"]) if "obj_id" in request.GET else None
#    if obj != None:
#        obj.delete()
#    items = RouteExt.objects.filter(external_manager=request.user.employee.company)
#    return render(request, "operations/external/routes-list.html", {"routes_ext": items})
#
#@group_required("external",)
#def facility_external(request):
#    items = Facility.objects.filter(company=request.user.employee.company)
#    return render(request, "operations/external/facilities.html", {"facilities": items})
#
#@group_required("external",)
#def facility_waste_external(request):
#    fac = get_or_none(Facility, get_param(request.GET, "obj_id"))
#    return render(request, "operations/external/facility-waste.html", {"item_list": fac.waste.filter(toRoute=False),})
#
