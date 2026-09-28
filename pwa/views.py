from django.shortcuts import render, redirect
from django.urls import reverse
#from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

from datetime import datetime
from gesplan.decorators import group_required_pwa
from gesplan.commons import user_in_group, get_or_none, get_param, show_exc
from gestion.models import Employee, EmployeeAccessLog, EmployeeTruck, EmployeeTruckKm, Truck


@group_required_pwa("drivers", "drivers_mpl", "operators", "external")
def index(request):
    try:
        if user_in_group(request.user, "operators"):
            return redirect(reverse('pwa-operator'))
        if user_in_group(request.user, "drivers"):
            return redirect(reverse('pwa-driver'))
        if user_in_group(request.user, "drivers_mpl"):
            return redirect(reverse('pwa-driver-mpl'))
        if user_in_group(request.user, "external"):
            return redirect(reverse('pwa-external'))
    except:
        return redirect(reverse('pwa-login'))

@group_required_pwa("drivers", "drivers_mpl", "operators")
def access_log(request):
    finish_param = get_param(request.GET, "finish")
    location = get_param(request.GET, "location")
    finish = True if finish_param == "True" else False
    emp = request.user.employee
    log = EmployeeAccessLog.objects.filter(employee=emp, finish=False).first()
    #Hay una jornada empezada y se debe terminar
    if log != None and finish:
        EmployeeAccessLog.objects.create(employee=emp, location=location, finish=finish)
    #No hay una jornada empezada y se debe iniciar
    elif log == None and not finish:
        EmployeeAccessLog.objects.create(employee=emp, location=location, finish=finish)
    return HttpResponse("")

def pin_login(request):
    CONTROL_KEY = "SZRf2QMpIfZHPEh0ib7YoDlnnDp5HtjDqbAw"
    msg = ""  
    if request.method == "POST":
        context =  {}
        msg = "Operación no permitida"
        pin = request.POST.get('pin', None)
        control_key = request.POST.get('control_key', None)
        if pin != None and control_key != None:
            if control_key == CONTROL_KEY:
                try:
                    emp = get_or_none(Employee, pin, "pin")
                    login(request, emp.user)
                    request.session['pwa_app_session'] = True
                    if emp.is_operator:
                        return redirect(reverse('pwa-operator'))
                    if emp.is_driver:
                        return redirect(reverse('pwa-driver'))
                    if emp.is_driver_mpl:
                        return redirect(reverse('pwa-driver-mpl'))
                    if emp.is_external:
                        return redirect(reverse('pwa-external'))

                    return HttpResponse("OK {}".format(emp.name))
                except Exception as e:
                    msg = "Pin no válido"
                    print(e)
            else:
                msg = "Bad control"
            
        #return render(request, "mobile/error.html", {'msg':msg})
    #else:
    return render(request, "pwa-login.html", {'msg': msg})

@group_required_pwa("drivers", "drivers_mpl", "operators")
def pin_logout(request):
    return render(request, "pwa-logout.html", {'now': datetime.now()})

@group_required_pwa("drivers", "drivers_mpl", "operators", "external")
def pin_logout_confirm(request):
    logout(request)
    return redirect(reverse('pwa-login'))

'''
    TRUCK
'''
@group_required_pwa("drivers", "drivers_mpl")
def select_truck(request):
    truck_list = Truck.objects.filter(company=request.user.employee.company)
    return render(request, "pwa-select-truck.html", {'truck_list': truck_list})

@group_required_pwa("drivers", "drivers_mpl")
def save_truck(request):
    try:
        truck = Truck.objects.filter(
            pk=get_param(request.POST, "truck"),
            company=request.user.employee.company,
        ).first()
        if truck != None:
            #Quitamos el camión a otro empleado si lo tiene asignado
            et_aux = EmployeeTruck.objects.filter(truck=truck).first()
            if et_aux != None:
                et_aux.truck = None
                et_aux.save()
            #Asignamos el caminón al operador
            et, created = EmployeeTruck.objects.get_or_create(employee=request.user.employee)
            et.truck = truck
            et.save()
            #EmployeeTruck.objects.create(employee=request.user.employee, truck=truck)

            if et.employee.is_driver:
                return redirect(reverse('pwa-driver'))
            if et.employee.is_driver_mpl:
                return redirect(reverse('pwa-driver-mpl'))
            return redirect("pwa-home")
        else:
            return (render(request, "error_exception.html", {'exc': 'Truck not found!'}))
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("drivers", "drivers_mpl")
def set_km(request):
    return render(request, "pwa-set-km.html", {})

@group_required_pwa("drivers", "drivers_mpl")
def save_km(request):
    try:
        km = get_param(request.POST, "km")
        emp = request.user.employee
        etkm = EmployeeTruckKm.objects.create(employee=emp, truck=emp.truck, km=km)

        if emp.is_driver:
            return redirect(reverse('pwa-driver'))
        if emp.is_driver_mpl:
            return redirect(reverse('pwa-driver-mpl'))
        return redirect("pwa-home")
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))


#from gestion.models import Employment, Facility, WasteInFacility, PointRoute, Waste, Workday, Route
#from incidents.models import Incident, IncidentType
#from citizens.models import Citizen,Town, WasteCitizen
#from tray.models import TrayTrack
#from simpromi.commons import show_exc
#from minipuntos.models import MinipointAction
#from .forms import MinipointActionForm
#
#import requests, json, datetime, string, random
#import django.utils.timezone as tz

#@group_required_pwa("drivers", "operators")
#def manager_home(request):
#    return render(request, "managers/home.html")

#'''
#    OPERATORS
#'''
#@login_required(login_url="/pwa/login/")
#def operator_home(request):
#    return render(request, "operators/home.html")
#
#@login_required(login_url="/pwa/login/")
#def operator_wastes(request):
#    user = request.user.employment
#    if user.is_worker:
#        wif = WasteInFacility.objects.filter(facility=user.facility)
#        return render(request, "operators/containers.html", {'waste_list':wif})
#    else:
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_waste_edit(request, waste_id=None):
#    try:
#        user = request.user.employment
#        if user.is_worker:
#            if waste_id is not None:
#                wif = WasteInFacility.objects.get(pk=waste_id)
#                return render(request, "operators/pwa-waste-form.html", {'wif':wif})
#            else:
#                return redirect(reverse('pwa-operator-waste'))
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_waste_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_worker:
#                waste_id = request.POST.get('waste_id', None)
#                if waste_id is not None:
#                    wif = WasteInFacility.objects.get(pk=waste_id)
#                    wif.filling_degree = float(request.POST.get("filling_degree", wif.filling_degree))
#                    wif.save()
#                    return redirect(reverse('pwa-operator-waste'))
#                else:
#                    return redirect(reverse('pwa-operator-waste'))
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_routes(request):
#    user = request.user.employment
#    if user.is_worker:
#        date = datetime.datetime.today().strftime("%Y-%m-%d")
#        route_list = PointRoute.objects.filter(facility=user.facility, route__date=date).order_by('ordering')
#        return render(request, "operators/routes.html", {'route_list':route_list})
#    else:
#        return redirect(reverse('pwa-home'))
##    try:
##        api_endpoint = "https://{}/{}".format(request.META['HTTP_HOST'], reverse('get_facility_trucks_for_date'))
##        data={'params':json.dumps({'date':datetime.datetime.now().strftime('%d-%m-%Y'), 'pin':request.user.employment.pin})}
##        response = requests.post(api_endpoint, data=data)
##        data = json.loads(response.text)
##        return (render(request, "operators/routes.html", {'data':data}))
##    except Exception as e:
##        print (show_exc(e))
##        return render(request, "full_error_exception.html", {'exc':show_exc(e)})
##
#@login_required(login_url="/pwa/login/")
#def operator_route_check(request, route_id=None):
#    try:
#        point = PointRoute.objects.get(pk=route_id)
#        if (point.facility == request.user.employment.facility):
#            api_endpoint = "https://{}/{}".format(request.META['HTTP_HOST'], reverse('update_trucks_validation'))
#            data={'params':json.dumps({'data':json.dumps([{'pk':point.pk,'modified':datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),'verified_operator':datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]), 'pin':request.user.employment.pin})}
#            response = requests.post(api_endpoint, data=data)
#            data = json.loads(response.text)
#            print (data)
#            return redirect(reverse('pwa-operator-route'))
#        else:
#            return redirect(reverse('pwa-operator-route'))
#        api_endpoint = "https://{}/{}".format(request.META['HTTP_HOST'], reverse('get_facility_trucks_for_date'))
#        data={'params':json.dumps({'date':'25-11-2021', 'pin':request.user.employment.pin})}
#        response = requests.post(api_endpoint, data=data)
#        data = json.loads(response.text)
#        return (render(request, "operators/routes.html", {'data':data}))
#    except Exception as e:
#        print (show_exc(e))
#        return render(request, "full_error_exception.html", {'exc':show_exc(e)})
#
#@login_required(login_url="/pwa/login/")
#def operator_incidents(request):
#    user = request.user.employment
#    if user.is_worker:
#        incident_list = Incident.objects.filter(owner=request.user)
#        return render(request, "operators/incidents.html", {'incident_list':incident_list})
#    else:
#        return redirect(reverse('pwa-home'))
#
#def get_incident_code():
#    code =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
#    while Incident.objects.filter(code=code).exists():
#        code =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
#    return code
#
#@login_required(login_url="/pwa/login/")
#def operator_incident_edit(request, incident_id=None):
#    try:
#        user = request.user.employment
#        if user.is_worker:
#            incident = Incident.objects.get(pk=incident_id) if incident_id is not None else None
#            #else:
#            #    incident = Incident.objects.create(owner = request.user, code = get_incident_code())
#            return render(request, "operators/pwa-incident-form.html", {'incident': incident, 'type_list': IncidentType.objects.all()})
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_incident_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_worker:
#                type_id = float(request.POST.get("type", ""))
#                incident_type = IncidentType.objects.get(pk = type_id) if type_id != "" else None 
#
#                incident_id = request.POST.get('incident_id', None)
#                #obj = Incident.objects.get(pk=incident_id) if incident_id != None else Incident.objects.create(owner=request.user, code=get_incident_code())
#                if incident_id != None and incident_id != "":
#                    obj = Incident.objects.get(pk=incident_id)
#                else:
#                    obj = Incident.objects.create(owner=request.user, code=get_incident_code(), creation_date=datetime.datetime.now())
#                obj.subject = request.POST.get("subject", obj.subject)
#                obj.description = request.POST.get("description", obj.description)
#                obj.type = incident_type
#                obj.save()
#                return redirect(reverse('pwa-operator-incidents'))
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_citizens(request):
#    user = request.user.employment
#    if user.is_worker:
#        now = datetime.datetime.now()
#        is_monday = datetime.datetime.today().weekday() == 0
#        is_saturday = datetime.datetime.today().weekday() == 5
#        start_shift = now.replace(hour=00, minute=1)
#        end_shift = now.replace(hour=13, minute=59)
#        if is_monday:
#            end_shift = now.replace(hour=16, minute=29)
#        elif is_saturday:
#            end_shift = now.replace(hour=14, minute=29)	
#        if (now > end_shift):
#            start_shift = start_shift.replace(hour=14, minute=00)
#            if is_monday:
#                start_shift=start_shift.replace(hour=16, minute=30)
#            elif is_saturday:
#                start_shift=start_shift.replace(hour=14, minute=30)
#            end_shift = end_shift.replace(hour=23, minute=59)
#				
#        citizen_list = Citizen.objects.filter(facility = user.facility, date__gte=start_shift, date__lte=end_shift).order_by('-pk')
#        return render(request, "operators/citizens.html", {'citizen_list': citizen_list, 'today': now})
#    else:
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_citizen_edit(request, citizen_id=None):
#    try:
#        user = request.user.employment
#        if user.is_worker:
#            citizen = Citizen.objects.get(pk=citizen_id) if citizen_id is not None else None
#            now = datetime.datetime.now()
#            return render(request, "operators/pwa-citizen-form.html", {'citizen': citizen, 'town_list': Town.objects.all(), 'today': now})
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_citizen_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_worker:
#                town_id = float(request.POST.get("town", ""))
#                town = Town.objects.get(pk = town_id) if town_id != "" else None 
#
#                citizen_id = request.POST.get('citizen_id', None)
#                if citizen_id != None and citizen_id != "":
#                    obj = Citizen.objects.get(pk=citizen_id)
#                else:
#                    obj = Citizen.objects.create(employment=user, facility=user.facility)
#                obj.identification = request.POST.get("identification", obj.identification)
#                obj.phone = request.POST.get("phone", obj.phone)
#                obj.plate = request.POST.get("plate", obj.plate)
#                obj.address = request.POST.get("address", obj.address)
#                obj.observations = request.POST.get("observations", obj.observations)
#                obj.town = town
#                obj.save()
#                #return redirect(reverse('pwa-operator-citizens'))
#                return redirect("pwa-operator-citizen-waste", obj.id)
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_citizen_remove(request, citizen_id):
#    try:
#        user = request.user.employment
#        if user.is_worker:
#            citizen = Citizen.objects.get(pk=citizen_id)
#            citizen.delete()
#            now = datetime.datetime.now()
#            #return render(request, "operators/citizens.html", {'citizen_list': citizen_list, 'today': now})
#            return redirect("pwa-operator-citizens")
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#
#@login_required(login_url="/pwa/login/")
#def operator_citizen_waste(request, citizen_id, waste_id="", units="", msg=""):
#    user = request.user.employment
#    if user.is_worker:
#        citizen = Citizen.objects.get(pk = citizen_id)  
#        return render(request, "operators/pwa-citizen-waste-form.html", {'citizen': citizen, 'waste_list': Waste.objects.all(), 'waste_id':waste_id, 'units': units, 'msg': msg})
#    return redirect(reverse('pwa-home'))
# 
#@login_required(login_url="/pwa/login/")
#def operator_citizen_waste_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_worker:
#                accept = request.POST["accept"] if "accept" in request.POST else ""
#                now = datetime.datetime.now()
#                start_shift = now.replace(hour=00, minute=1)
#                end_shift = now.replace(hour=23, minute=59)
#                citizen = Citizen.objects.get(pk=request.POST["citizen_id"])
#                waste = Waste.objects.get(pk=request.POST["waste"])
#                units = WasteCitizen.objects.filter(citizen__plate__iexact=citizen.plate, citizen__date__gte=start_shift, citizen__date__lte=end_shift, waste=waste).aggregate(Sum('units'))['units__sum']
#                total_units = 0
#                form_units = 0.0
#                if units != None:
#                    total_units += units
#                if "units" in request.POST and request.POST["units"] != "":
#                    form_units = float(request.POST["units"])
#                    total_units += form_units
#                if total_units > waste.day_limit and accept == "":
#                    msg = "Superado el límite diario de {} del residuo {}<br/>".format(waste.day_limit, waste.name)
#                    waste_list = WasteCitizen.objects.filter(citizen__plate__iexact=citizen.plate, citizen__date__gte=start_shift, citizen__date__lte=end_shift, waste=waste)
#                    for item in waste_list:
#                        msg += "- {}: {}<br/>".format(item.citizen.facility, item.units)
#                    return redirect("pwa-operator-citizen-waste", citizen.id, waste.id, form_units, msg)
#                else:
#                    obj = WasteCitizen.objects.create(citizen=citizen, waste=waste, units=request.POST["units"])
#                    return redirect("pwa-operator-citizen-waste", citizen.id)
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_citizen_waste_remove(request, waste_id):
#    user = request.user.employment
#    if user.is_worker:
#        waste = WasteCitizen.objects.get(pk = waste_id)  
#        citizen = waste.citizen
#        waste.delete()
#        return redirect("pwa-operator-citizen-waste", citizen.id)
#    return redirect(reverse('pwa-home'))
# 
#@login_required(login_url="/pwa/login/")
#def operator_citizen_waste_end(request, citizen_id):
#    try:
#        citizen = Citizen.objects.get(pk=citizen_id)
#        if citizen.wastes.all().count() == 0:
#            citizen.delete()
#    except Exception as e:
#        print(e)
#    return redirect("pwa-operator-citizens")
#
#@login_required(login_url="/pwa/login/")
#def operator_sessions(request):
#    sessions = request.user.employment.get_current_workday()
#    return render(request, "operators/sessions.html", {'sessions': sessions})
#
#@login_required(login_url="/pwa/login/")
#def operator_ini_workday(request):
#    user = request.user.employment
#    if user.is_worker:
#        location = request.POST["location"] if "location" in request.POST else ""
#        workday = Workday.objects.create(employment=user, ini_date=datetime.datetime.now(), ini_loc=location)
#    return redirect(reverse('pwa-operator-sessions'))
#    #return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def operator_end_workday(request):
#    user = request.user.employment
#    if user.is_worker:
#        workday_list = user.get_current_workday()
#        workday = workday_list.last()
#        if workday != None:
#            location = request.POST["location"] if "location" in request.POST else ""
#            workday.end_date = datetime.datetime.now()
#            workday.end_loc = location
#            workday.save()
#    return redirect(reverse('pwa-operator-sessions'))
#    #return redirect(reverse('pwa-home'))
#
#'''
#    DRIVERS
#'''
#@login_required(login_url="/pwa/login/")
#def driver_home(request):
#    return render(request, "drivers/home.html")
#
#@login_required(login_url="/pwa/login/")
#def driver_incidents(request):
#    user = request.user.employment
#    if user.is_driver:
#        incident_list = Incident.objects.filter(owner=request.user)
#        return render(request, "drivers/incidents.html", {'incident_list':incident_list})
#    else:
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_incident_edit(request, incident_id=None):
#    try:
#        user = request.user.employment
#        if user.is_driver:
#            incident = Incident.objects.get(pk=incident_id) if incident_id is not None else None
#            return render(request, "drivers/pwa-incident-form.html", {'incident': incident, 'type_list': IncidentType.objects.all()})
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_incident_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_driver:
#                type_id = float(request.POST.get("type", ""))
#                incident_type = IncidentType.objects.get(pk = type_id) if type_id != "" else None 
#
#                incident_id = request.POST.get('incident_id', None)
#                if incident_id != None and incident_id != "":
#                    obj = Incident.objects.get(pk=incident_id)
#                else:
#                    obj = Incident.objects.create(owner=request.user, code=get_incident_code(), creation_date=datetime.datetime.now())
#                obj.subject = request.POST.get("subject", obj.subject)
#                obj.description = request.POST.get("description", obj.description)
#                obj.type = incident_type
#                obj.save()
#                return redirect(reverse('pwa-driver-incidents'))
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_trays(request):
#    user = request.user.employment
#    if user.is_driver:
#        facility = Facility.objects.get(code="EXP")
#        traytrack_list = TrayTrack.objects.filter(location__distance_lte=(facility.location, D(m=200)), valid=True).order_by("-date")
#        return render(request, "drivers/trays.html", {'traytrack_list': traytrack_list})
#    else:
#        return redirect(reverse('pwa-home'))
#
##@login_required(login_url="/pwa/login/")
##def driver_tray_edit(request, tray_id=None):
##    try:
##        user = request.user.employment
##        if user.is_driver:
##            tt = TrayTruck.objects.get(pk=tray_id) if tray_id is not None else None
##            return render(request, "drivers/pwa-tray-form.html", {'traytrack': tt})
##        else:
##            return redirect(reverse('pwa-home'))
##    except Exception as e:
##        print (show_exc(e))
##        return redirect(reverse('pwa-home'))
##
##@login_required(login_url="/pwa/login/")
##def driver_tray_save(request):
##    try:
##        if request.method == "POST":
##            user = request.user.employment
##            if user.is_driver:
##                type_id = float(request.POST.get("type", ""))
##                incident_type = IncidentType.objects.get(pk = type_id) if type_id != "" else None 
##
##                incident_id = request.POST.get('incident_id', None)
##                if incident_id != None and incident_id != "":
##                    obj = Incident.objects.get(pk=incident_id)
##                else:
##                    obj = Incident.objects.create(owner=request.user, code=get_incident_code(), creation_date=datetime.datetime.now())
##                obj.subject = request.POST.get("subject", obj.subject)
##                obj.description = request.POST.get("description", obj.description)
##                obj.type = incident_type
##                obj.save()
##                return redirect(reverse('pwa-driver-incidents'))
##        return redirect(reverse('pwa-home'))
##    except Exception as e:
##        print (show_exc(e))
##        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_routes(request):
#    user = request.user.employment
#    if user.is_driver:
#        route_list = Route.objects.filter(driver__employment = request.user.employment).order_by('-date')[:10]
#        return render(request, "drivers/routes.html", {'route_list': route_list})
#    else:
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_route_view(request, route_id):
#    from django.contrib.gis.geos import fromstr
#
#    try:
#        user = request.user.employment
#        if user.is_driver:
#            route = Route.objects.get(pk=route_id) if route_id is not None else None
#            return render(request, "drivers/pwa-route-view.html", {'route': route})
#        else:
#            return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_ini_route(request):
#    user = request.user.employment
#    if user.is_driver:
#        try:
#            lat = request.POST["lat"] if "lat" in request.POST else ""
#            lon = request.POST["lon"] if "lon" in request.POST else ""
#            route_id = request.POST["route"] if "route" in request.POST else ""
#            route = Route.objects.get(id=route_id)
#            route.start_location = Point(float(lat), float(lon))
#            route.start_time = datetime.datetime.now().strftime('%H:%M:%S') 
#            route.save()
#            return redirect(reverse('pwa-driver-route-view', kwargs={'route_id':route.id}))
#        except Exception as e:
#            print(e)
#    return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_end_route(request):
#    user = request.user.employment
#    if user.is_driver:
#        try:
#            lat = request.POST["lat"] if "lat" in request.POST else ""
#            lon = request.POST["lon"] if "lon" in request.POST else ""
#            route_id = request.POST["route"] if "route" in request.POST else ""
#            route = Route.objects.get(id=route_id)
#            route.end_location = Point(float(lat), float(lon))
#            route.end_time = datetime.datetime.now().strftime('%H:%M:%S') 
#            route.save()
#            return redirect(reverse('pwa-driver-route-view', kwargs={'route_id':route.id}))
#        except Exception as e:
#            print(e)
#    return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_check_point(request, point_id):
#    user = request.user.employment
#    if user.is_driver:
#        try:
#            point = PointRoute.objects.get(id=point_id)
#            limit_date = datetime.datetime(9999, 12, 31, 23, 59)
#            dd = point.verified_driver
#            driver_date = datetime.datetime(dd.year, dd.month, dd.day, dd.hour, dd.minute) 
#            if driver_date == limit_date: 
#                point.verified_driver = tz.now()
#                check_weight = True
#            else:
#                point.verified_driver = tz.datetime.max
#                check_weight = False
#            point.save()
#
#            waste_code = point.waste.code if point.waste != None else ""
#            if point.facility.fac_type.code == "MPL" and waste_code not in ["MPLMOVE", "MPLCLEAN"] and check_weight:
#                forms = []
#                for waste in point.facility.waste.all():
#                    try:
#                        mini = MinipointAction.objects.get(wasteinfac=waste, route=point.route)
#                    except:
#                        mini = MinipointAction(wasteinfac=waste, weight=0, route=point.route)
#                    form = MinipointActionForm(instance=mini)
#                    forms.append(form)
#                return render(request, "drivers/pwa-minipointaction-form.html", {'forms':forms, 'route':point.route})
#            else:
#                return redirect(reverse('pwa-driver-route-view', kwargs={'route_id':point.route.id}))
#        except Exception as e:
#            print(e)
#    return redirect(reverse('pwa-home'))
#
#@login_required
#def driver_minipoint_weight_save(request):
#    try:
#        if request.method == "POST":
#            try:
#                item_id = request.POST.get("minipointaction-id", None)
#                instance = MinipointAction.objects.get(pk=item_id)
#            except:
#                instance = MinipointAction()
#            form = MinipointActionForm(request.POST, instance=instance)
#            if form.is_valid():
#                form.save()
#                return HttpResponse("<div class='alert alert-success save-is-ok'><i class='fas fa-check-circle'></div>")
#            else:
#                return HttpResponse("<div class='alert alert-danger save-is-wrong'><i class='fas fa-times-circle'></div>")
#    except Exception as e:
#        return (render(request, "full_error_exception.html", {'exc':show_exc(e)}))
#
#@login_required(login_url="/pwa/login/")
#def driver_update_amount(request):
#    if request.POST:
#        try:
#            item = PointRoute.objects.get(pk=request.POST["id"])
#            amount = request.POST["amount"]
#            item.weight = float(amount.replace(",", "."))
#            item.save()
#            return redirect(reverse('pwa-driver-route-view', kwargs={'route_id':item.route.id}))
#        except Exception as e:
#            print(e)
#    return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_view_doc(request, point_id):
#    user = request.user.employment
#    if user.is_driver:
#        try:
#            point = PointRoute.objects.get(id=point_id)
#            datas = point.jsonDoc()
#            return render(request, "drivers/driver_doc.html", {"datas": datas})
#            #return render(request, "drivers/driver_doc.html", {})
#        except Exception as e:
#            print(e)
#    return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_exp(request):
#    user = request.user.employment
#    if user.is_driver:
#        item = Facility.objects.filter(code = "EXP").first()
#        return render(request, "drivers/exp.html", {'item': item})
#    else:
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_wif_edit(request, waste_id):
#    try:
#        wif = WasteInFacility.objects.get(pk=waste_id)
#        return render(request, "drivers/pwa-waste-edit.html", {'wif': wif, 'waste_list': Waste.objects.all()})
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_wif_save(request):
#    try:
#        if request.method == "POST":
#            user = request.user.employment
#            if user.is_driver:
#                waste_id = float(request.POST.get("waste", ""))
#                waste = Waste.objects.get(pk = waste_id) if waste_id != "" else None 
#
#                wif_id = request.POST.get('wif_id', None)
#                obj = WasteInFacility.objects.get(pk=wif_id)
#                obj.waste = waste
#                obj.filling_degree = float(request.POST.get("filling_degree", "").replace(",", "."))
#                obj.save()
#                return redirect(reverse('pwa-driver-exp'))
#        return redirect(reverse('pwa-home'))
#    except Exception as e:
#        print (show_exc(e))
#        return redirect(reverse('pwa-home'))
#
#@login_required(login_url="/pwa/login/")
#def driver_manage_routes(request):
#    request.session["pwa_base"] = "pwa_base.html"
#    return redirect(reverse('routes'))
#
#
#'''
#    STORAGE
#'''
##@login_required(login_url="/pwa/login/")
#def storage_save(request):
#    return render(request, "operators/save-local.html", {'date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
#
##@login_required(login_url="/pwa/login/")
#def storage_load(request):
#    return render(request, "operators/read-local.html")
#
##@login_required(login_url="/pwa/login/")
#def storage_reset(request):
#    return render(request, "operators/reset-local.html")
