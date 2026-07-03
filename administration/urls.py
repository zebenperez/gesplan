from django.urls import path
from . import views 

urlpatterns = [ 
    #path('home', views.index, name='citizens-index'),

    #---------------------- CONTRACTS -----------------------
    path('contracts', views.contracts, name='contracts'),
    path('contracts/list', views.contracts_list, name='contracts-list'),
    path('contracts/search', views.contracts_search, name='contracts-search'),
    path('contracts/form', views.contracts_form, name='contracts-form'),
    path('contracts/remove', views.contracts_remove, name='contracts-remove'),

    #---------------------- LOTS -----------------------
    path('contracts/lots/<int:obj_id>', views.contracts_lots, name='contracts-lots'),
    path('contracts/lots/list', views.contracts_lots_list, name='contracts-lots-list'),
    path('contracts/lots/form', views.contracts_lots_form, name='contracts-lots-form'),
    path('contracts/lots/remove', views.contracts_lots_remove, name='contracts-lots-remove'),
    path('contracts/lots/upload', views.contracts_lots_upload, name='contracts-lots-upload'),
    path('contracts/lots/file-remove', views.contracts_lots_file_remove, name='contracts-lots-file-remove'),

    #---------------------- INVOICES -----------------------
    path('contracts/invoices/<int:obj_id>', views.contracts_invoices, name='contracts-invoices'),
    path('contracts/invoices/list', views.contracts_invoices_list, name='contracts-invoices-list'),
    path('contracts/invoices/form', views.contracts_invoices_form, name='contracts-invoices-form'),
    path('contracts/invoices/remove', views.contracts_invoices_remove, name='contracts-invoices-remove'),
    path('contracts/invoices/upload', views.contracts_invoices_upload, name='contracts-invoices-upload'),
    path('contracts/invoices/file-remove', views.contracts_invoices_file_remove, name='contracts-invoices-file-remove'),

    #---------------------- REPORTS -----------------------
    path('contracts-report', views.contracts_report, name='contracts-report'),
    path('contracts-report-search', views.contracts_report_search, name='contracts-report-search'),
    path('facilities-report', views.facilities_report, name='facilities-report'),
    path('facilities-report-search', views.facilities_report_search, name='facilities-report-search'),
    path('vehicles-report', views.vehicles_report, name='vehicles-report'),
    path('vehicles-report-search', views.vehicles_report_search, name='vehicles-report-search'),
]

