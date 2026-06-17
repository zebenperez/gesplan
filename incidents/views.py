from django.http import HttpResponse
from django.shortcuts import render, redirect

from gesplan.decorators import group_required
from gesplan.commons import get_float, get_or_none, get_param, get_session, set_session, show_exc, user_in_group
from .models import Incident, IncidentType


@group_required("admins", "external", "cabildo", "managers")
def index(request):
    if user_in_group(request.user, "cabildo"):
        return redirect("operation-index-cabildo")
    if user_in_group(request.user, "external"):
        return redirect("operation-index-external")
    return render(request, "index.html")



