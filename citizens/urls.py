from django.urls import path
from . import views 

urlpatterns = [ 
    path('reports', views.index, name='report-index'),

    #---------------------- CITIZENS -----------------------
    path('', views.citizens_login),
    path('citizens', views.citizens, name='citizens'),
    path('citizens/info/', views.citizens_info, name='citizens-info'),
    path('citizens/info2/', views.citizens_info2, name='citizens-info2'),
    path('citizens/list', views.citizens_list, name='citizens-list'),
    path('citizens/search', views.citizens_search, name='citizens-search'),
    path('citizens/form', views.citizens_form, name='citizens-form'),
    path('citizens/remove', views.citizens_remove, name='citizens-remove'),
    path('citizens/report/', views.citizens_report, name='citizens-report'),
    path('citizens/report/<slug:uuid>/', views.citizens_report, name='citizens-report'),
    path('citizens/report/check-cert/<slug:uuid>', views.citizens_check_certificate, name='citizens-report-check-cert'),
    path('citizens/cert/', views.citizens_report_cert, name='citizens-report-cert'),
    path('citizens/status-containers/', views.citizens_status_containers, name='citizens-status-containers'),
    path('citizens/sign-up/', views.citizens_signup, name='citizens-signup'),
    path('citizens/login/', views.citizens_login, name='citizens-login'),
    path('citizens/logout/', views.citizens_logout, name='citizens-logout'),





    #---------------------- COMPANIES -----------------------
    #path('companies', views.companies, name='companies'),
    #path('companies/list', views.companies_list, name='companies-list'),
    #path('companies/search', views.companies_search, name='companies-search'),
    #path('companies/form', views.companies_form, name='companies-form'),
    #path('companies/remove', views.companies_remove, name='companies-remove'),
]

