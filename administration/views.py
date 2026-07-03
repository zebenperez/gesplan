from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Exists, OuterRef

from datetime import datetime

from gesplan.decorators import group_required
from gesplan.commons import get_float, get_or_none, get_param, get_session, set_session, show_exc
from .models import Contract, ContractStatus, ContractLot, Invoice, Epigraph
from gesplan.commons import show_exc


#@group_required("admins",)
#def index(request):
#    return render(request, "index.html")

'''
    CONTRACTS
'''
def get_contracts(request):
    number = get_session(request, "s_contract_number")
#    idate = get_session(request, "s_citizen_idate")
#    edate = get_session(request, "s_citizen_edate")
    status = get_session(request, "s_contract_status")
#    if idate == "":
#        idate = datetime.now().replace(hour=0, minute=0, second=0)
#        set_session(request, "s_citizen_idate", idate.strftime("%d-%m-%Y"))
#    if edate == "":
#        edate = datetime.now().replace(hour=23, minute=59, second=59)
#        set_session(request, "s_citizen_edate", idate.strftime("%d-%m-%Y"))
#    kwargs = {"date__range": (idate, edate)}
    kwargs = {}
    if number != "":
        kwargs["number__icontains"] = number
    if status != "":
        kwargs["status__id"] = status
    #print(kwargs)
    return Contract.objects.filter(**kwargs)

def get_contracts_context(request):
    return {
        "items": get_contracts(request),
        "status_list": ContractStatus.objects.all()
    }

@group_required("admins",)
def contracts(request):
    return render(request, "contracts/contracts.html", get_contracts_context(request))

@group_required("admins",)
def contracts_list(request):
    return render(request, "contracts/contracts-list.html", get_contracts_context(request))

@group_required("admins",)
def contracts_search(request):
    #set_session(request, "s_citizen_idate", get_param(request.GET, "s_citizen_idate"))
    #set_session(request, "s_citizen_edate", get_param(request.GET, "s_citizen_edate"))
    set_session(request, "s_contract_number", get_param(request.GET, "s_contract_number"))
    set_session(request, "s_contract_status", get_param(request.GET, "s_contract_status"))
    return render(request, "contracts/contracts-list.html", get_contracts_context(request))

@group_required("admins",)
def contracts_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Contract, obj_id)
    if obj == None:
        obj = Contract.objects.create()
    return render(request, "contracts/contracts-form.html", {'obj': obj, "status_list": ContractStatus.objects.all()})

@group_required("admins",)
def contracts_remove(request):
    obj = get_or_none(Contract, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.delete()
    return render(request, "contracts/contracts-list.html", get_contracts_context(request))

'''
   CONTRACTS LOTS 
'''
def get_contracts_lots_context(contract):
    context = {
        "items": ContractLot.objects.filter(contract=contract),
        "contract": contract
    }
    return context

@group_required("admins",)
def contracts_lots(request, obj_id):
    obj = get_or_none(Contract, obj_id)
    return render(request, "contracts/lots/lots.html", get_contracts_lots_context(obj))

@group_required("admins",)
def contracts_lots_list(request):
    obj = get_or_none(Contract, get_param(request.GET, "obj_id"))
    return render(request, "contracts/lots/lots-list.html", get_contracts_lots_context(obj))

@group_required("admins",)
def contracts_lots_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(ContractLot, obj_id)
    if obj == None:
        contract = get_or_none(Contract, get_param(request.GET, "contract"))
        obj = ContractLot.objects.create(contract=contract)
        
    context = {'obj':obj, "epi_list":Epigraph.objects.all()}
    return render(request, "contracts/lots/lots-form.html", context)

@group_required("admins",)
def contracts_lots_remove(request):
    obj = get_or_none(ContractLot, request.GET["obj_id"]) if "obj_id" in request.GET else None
    contract = obj.contract
    if obj != None:
        obj.file.delete(save=True)
        obj.delete()
    return render(request, "contracts/lots/lots-list.html", get_contracts_lots_context(contract))

@group_required("admins",)
def contracts_lots_upload(request):
    obj = get_or_none(ContractLot, get_param(request.POST, "obj_id"))
    if obj != None:
        obj.file = request.FILES['file']
        obj.save()
    return render(request, "contracts/lots/lots-file.html", {"obj": obj})

@group_required("admins",)
def contracts_lots_file_remove(request):
    obj = get_or_none(ContractLot, get_param(request.GET, "obj_id"))
    if obj != None:
        obj.file.delete(save=True)
        obj.file = None
        obj.save()
    return render(request, "contracts/lots/lots-file.html", {"obj": obj})

'''
   CONTRACTS INVOICES
'''
def get_contracts_invoices_context(contract):
    context = {
        "items": Invoice.objects.filter(contract=contract),
        "contract": contract
    }
    return context

@group_required("admins",)
def contracts_invoices(request, obj_id):
    obj = get_or_none(Contract, obj_id)
    return render(request, "contracts/invoices/invoices.html", get_contracts_invoices_context(obj))

@group_required("admins",)
def contracts_invoices_list(request):
    obj = get_or_none(Contract, get_param(request.GET, "obj_id"))
    return render(request, "contracts/invoices/invoices-list.html", get_contracts_invoices_context(obj))

@group_required("admins",)
def contracts_invoices_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Invoice, obj_id)
    if obj == None:
        contract = get_or_none(Contract, get_param(request.GET, "contract"))
        obj = Invoice.objects.create(contract=contract)
        
    context = {'obj':obj, "epi_list":Epigraph.objects.all()}
    return render(request, "contracts/invoices/invoices-form.html", context)

@group_required("admins",)
def contracts_invoices_remove(request):
    obj = get_or_none(Invoice, request.GET["obj_id"]) if "obj_id" in request.GET else None
    contract = obj.contract
    if obj != None:
        obj.file.delete(save=True)
        obj.delete()
    return render(request, "contracts/invoices/invoices-list.html", get_contracts_invoices_context(contract))

@group_required("admins",)
def contracts_invoices_upload(request):
    obj = get_or_none(Invoice, get_param(request.POST, "obj_id"))
    if obj != None:
        obj.file = request.FILES['file']
        obj.save()
    return render(request, "contracts/invoices/invoices-file.html", {"obj": obj})

@group_required("admins",)
def contracts_invoices_file_remove(request):
    obj = get_or_none(Invoice, get_param(request.GET, "obj_id"))
    if obj != None:
        obj.file.delete(save=True)
        obj.file = None
        obj.save()
    return render(request, "contracts/invoices/invoices-file.html", {"obj": obj})

'''
    CONTRACTS REPORTS
'''
def get_contracts_report(request):
    idate_ini = get_session(request, "sr_contract_idate_ini")
    idate_end = get_session(request, "sr_contract_idate_end")
    edate_ini = get_session(request, "sr_contract_edate_ini")
    edate_end = get_session(request, "sr_contract_edate_end")
    amount_ini = get_session(request, "sr_contract_amount_ini")
    amount_end = get_session(request, "sr_contract_amount_end")
    status = get_session(request, "sr_contract_status")
    epigraph = get_session(request, "sr_contract_epigraph")

    kwargs = {}
    if idate_ini != "":
        kwargs["ini_date__gte"] = idate_ini
    if idate_end != "":
        kwargs["ini_date__lte"] = idate_end
    if edate_ini != "":
        kwargs["end_date__gte"] = edate_ini
    if edate_end != "":
        kwargs["end_date__lte"] = edate_end
    if amount_ini != "":
        kwargs["amount__gte"] = get_float(amount_ini)
    if amount_end != "":
        kwargs["amount__lte"] = get_float(amount_end)
    if status != "":
        kwargs["contract__status__id"] = status
    if status != "":
        kwargs["epigraph__id"] = epigraph
    #print(kwargs)
    return ContractLot.objects.filter(**kwargs)

@group_required("admins",)
def contracts_report(request):
    context = {"items": [], "status_list": ContractStatus.objects.all(), "epigraph_list": Epigraph.objects.all()}
    return render(request, "contracts/reports/contracts.html", context)

@group_required("admins",)
def contracts_report_search(request):
    set_session(request, "sr_contract_idate_ini", get_param(request.GET, "sr_contract_idate_ini"))
    set_session(request, "sr_contract_idate_end", get_param(request.GET, "sr_contract_idate_end"))
    set_session(request, "sr_contract_edate_ini", get_param(request.GET, "sr_contract_edate_ini"))
    set_session(request, "sr_contract_edate_end", get_param(request.GET, "sr_contract_edate_end"))
    set_session(request, "sr_contract_amount_ini", get_param(request.GET, "sr_contract_amount_ini"))
    set_session(request, "sr_contract_amount_end", get_param(request.GET, "sr_contract_amount_end"))
    set_session(request, "sr_contract_status", get_param(request.GET, "sr_contract_status"))
    set_session(request, "sr_contract_epigraph", get_param(request.GET, "sr_contract_epigraph"))
    return render(request, "contracts/reports/contracts-list.html", {"items": get_contracts_report(request)})

@group_required("admins",)
def facilities_report(request):
    return HttpResponse("Función no implementada aún", status=501)
    try:
        context = {"items": [], "status_list": ContractStatus.objects.all(), "epigraph_list": Epigraph.objects.all()}
        return render(request, "contracts/reports/facilities.html", context)
    except Exception as e:
        print(show_exc(e))
        return HttpResponse(f"Error: {show_exc(e)}", status=500)

@group_required("admins",)
def facilities_report_search(request):
    set_session(request, "sr_contract_idate_ini", get_param(request.GET, "sr_contract_idate_ini"))
    set_session(request, "sr_contract_idate_end", get_param(request.GET, "sr_contract_idate_end"))
    set_session(request, "sr_contract_edate_ini", get_param(request.GET, "sr_contract_edate_ini"))
    set_session(request, "sr_contract_edate_end", get_param(request.GET, "sr_contract_edate_end"))
    set_session(request, "sr_contract_amount_ini", get_param(request.GET, "sr_contract_amount_ini"))
    set_session(request, "sr_contract_amount_end", get_param(request.GET, "sr_contract_amount_end"))
    set_session(request, "sr_contract_status", get_param(request.GET, "sr_contract_status"))
    set_session(request, "sr_contract_epigraph", get_param(request.GET, "sr_contract_epigraph"))
    return render(request, "contracts/reports/facilities-list.html", {"items": get_contracts_report(request)})

@group_required("admins",)
def vehicles_report(request):
    return HttpResponse("Función no implementada aún", status=501)
    context = {"items": [], "status_list": ContractStatus.objects.all(), "epigraph_list": Epigraph.objects.all()}
    return render(request, "contracts/reports/vehicles.html", context)  

@group_required("admins",)
def vehicles_report_search(request):
    set_session(request, "sr_contract_idate_ini", get_param(request.GET, "sr_contract_idate_ini"))
    set_session(request, "sr_contract_idate_end", get_param(request.GET, "sr_contract_idate_end"))
    set_session(request, "sr_contract_edate_ini", get_param(request.GET, "sr_contract_edate_ini"))
    set_session(request, "sr_contract_edate_end", get_param(request.GET, "sr_contract_edate_end"))
    set_session(request, "sr_contract_amount_ini", get_param(request.GET, "sr_contract_amount_ini"))
    set_session(request, "sr_contract_amount_end", get_param(request.GET, "sr_contract_amount_end"))
    set_session(request, "sr_contract_status", get_param(request.GET, "sr_contract_status"))
    set_session(request, "sr_contract_epigraph", get_param(request.GET, "sr_contract_epigraph"))
    return render(request, "contracts/reports/vehicles-list.html", {"items": get_contracts_report(request)})


