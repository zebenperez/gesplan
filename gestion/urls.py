#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.urls import path
from . import views, auto_views, operation_views, import_views

urlpatterns = [ 
    path('home', views.index, name='index'),

    #---------------------- COMPANIES -----------------------
    path('companies', views.companies, name='companies'),
    path('companies/list', views.companies_list, name='companies-list'),
    path('companies/search', views.companies_search, name='companies-search'),
    path('companies/form', views.companies_form, name='companies-form'),
    path('companies/remove', views.companies_remove, name='companies-remove'),

    #---------------------- FACILITIES -----------------------
    path('facilities/index', views.facilities_index, name='facilities-index'),
    path('facilities', views.facilities, name='facilities'),
    path('facilities/list', views.facilities_list, name='facilities-list'),
    path('facilities/search', views.facilities_search, name='facilities-search'),
    path('facilities/form', views.facilities_form, name='facilities-form'),
    path('facilities/remove', views.facilities_remove, name='facilities-remove'),

    path('facilities/items', views.facilities_items, name='facilities-items'),
    path('facilities/items-add', views.facilities_items_add, name='facilities-items-add'),
    path('facilities/items-return', views.facilities_items_return, name='facilities-items-return'),
    path('facilities/items-remove', views.facilities_items_remove, name='facilities-items-remove'),

    path('facilities/manteinances/<int:fac_id>', views.facilities_manteinances, name='facilities-manteinances'),
    path('facilities/manteinances/list', views.facilities_manteinances_list, name='facilities-manteinances-list'),
    path('facilities/manteinances/form', views.facilities_manteinances_form, name='facilities-manteinances-form'),
    path('facilities/manteinances/remove', views.facilities_manteinances_remove, name='facilities-manteinances-remove'),
    path('facilities/manteinances/upload', views.facilities_manteinances_upload, name='facilities-manteinances-upload'),
    path('facilities/manteinances/img-remove', views.facilities_manteinances_img_remove, name='facilities-manteinances-img-remove'),


    #---------------------- TRUCKS -----------------------
    path('trucks', views.trucks, name='trucks'),
    path('trucks/list', views.trucks_list, name='trucks-list'),
    path('trucks/search', views.trucks_search, name='trucks-search'),
    path('trucks/form', views.trucks_form, name='trucks-form'),
    path('trucks/remove', views.trucks_remove, name='trucks-remove'),

    path('trucks/manteinances/<int:truck_id>', views.trucks_manteinances, name='trucks-manteinances'),
    path('trucks/manteinances/list', views.trucks_manteinances_list, name='trucks-manteinances-list'),
    path('trucks/manteinances/form', views.trucks_manteinances_form, name='trucks-manteinances-form'),
    path('trucks/manteinances/remove', views.trucks_manteinances_remove, name='trucks-manteinances-remove'),
    path('trucks/manteinances/upload', views.trucks_manteinances_upload, name='trucks-manteinances-upload'),
    path('trucks/manteinances/img-remove', views.trucks_manteinances_img_remove, name='trucks-manteinances-img-remove'),


#    #---------------------- ROUTES -----------------------
#    path('routes', views.routes, name='routes'),
#    path('routes/list', views.routes_list, name='routes-list'),
#    path('routes/view', views.routes_view, name='routes-view'),
#    path('routes/search', views.routes_search, name='routes-search'),
#    path('routes/form', views.routes_form, name='routes-form'),
#    path('routes/remove', views.routes_remove, name='routes-remove'),

    #---------------------- EMPLOYEES -----------------------
    path('employees', views.employees, name='employees'),
    path('employees/list', views.employees_list, name='employees-list'),
    path('employees/search', views.employees_search, name='employees-search'),
    path('employees/form', views.employees_form, name='employees-form'),
    path('employees/save', views.employees_save, name='employees-save'),
    path('employees/remove', views.employees_remove, name='employees-remove'),
    path('employees/items', views.employees_items, name='employees-items'),
    path('employees/items-add', views.employees_items_add, name='employees-items-add'),
    path('employees/items-return', views.employees_items_return, name='employees-items-return'),
    path('employees/items-remove', views.employees_items_remove, name='employees-items-remove'),
    path('employees/contracts', views.employees_contracts, name='employees-contracts'),
    path('employees/contracts-add', views.employees_contracts_add, name='employees-contracts-add'),
    path('employees/contracts-remove', views.employees_contracts_remove, name='employees-contracts-remove'),

    #---------------------- ITEMS -----------------------
    path('items', views.items, name='items'),
    path('items/list', views.items_list, name='items-list'),
    path('items/search', views.items_search, name='items-search'),
    path('items/form', views.items_form, name='items-form'),
    path('items/form-amount', views.items_form_amount, name='items-form-amount'),
    path('items/form-amount/save', views.items_form_amount_save, name='items-form-amount-save'),
    path('items/remove', views.items_remove, name='items-remove'),
    path('items/location/<int:obj_id>/', views.items_location, name='items-location'),
    path('items/emps/search', views.items_emps_search, name='items-emps-search'),
    path('items/facs/search', views.items_facs_search, name='items-facs-search'),

    #---------------------- OPERATION -----------------------
    path('operation/index', operation_views.index, name='operation-index'),
    path('operation/incidents/list', operation_views.incidents_list, name='operation-incidents-list'),
    path('operation/routes/view', operation_views.routes_view, name='operation-routes-view'),
    path('operation/routes/list', operation_views.routes_list, name='operation-routes-list'),
    path('operation/routes-ext/list', operation_views.routes_ext_list, name='operation-routes-ext-list'),
    path('operation/routes/form', operation_views.routes_form, name='operation-routes-form'),
    path('operation/routes-ext/form', operation_views.routes_ext_form, name='operation-routes-ext-form'),
    path('operation/routes/remove', operation_views.routes_remove, name='operation-routes-remove'),
    path('operation/facility-waste', operation_views.facility_waste, name='operation-facility-waste'),
    path('operation/report', operation_views.report, name='operation-report'),
    path('operation/report-search', operation_views.report_search, name='operation-report-search'),
    path('operation/report-dir/<int:route_id>', operation_views.report_dir, name='operation-report-dir'),
    path('operation/routes/source-save', operation_views.routes_source_save, name='operation-routes-source-save'),
    path('operation/routes/img-upload', operation_views.routes_img_upload, name='operation-routes-img-upload'),
    path('operation/routes/img-remove', operation_views.routes_img_remove, name='operation-routes-img-remove'),

    path('operation/index-external', operation_views.index_external, name='operation-index-external'),
    path('operation/routes-external/list', operation_views.routes_external_list, name='operation-routes-external-list'),
    path('operation/routes-external/form', operation_views.routes_external_form, name='operation-routes-external-form'),
    path('operation/routes-external/facility-save', operation_views.routes_external_facility_save, name='operation-routes-facility-save'),
    path('operation/routes-external/remove', operation_views.routes_external_remove, name='operation-routes-external-remove'),
    path('operation/facility-external', operation_views.facility_external, name='operation-facility-external'),
    path('operation/facility-waste-external', operation_views.facility_waste_external, name='operation-facility-waste-external'),

    path('operation/index-cabildo', operation_views.index_cabildo, name='operation-index-cabildo'),
    path('operation/facility-waste-cabildo', operation_views.facility_waste_cabildo, name='operation-facility-waste-cabildo'),
    path('operation/routes/view-cabildo', operation_views.routes_view_cabildo, name='operation-routes-view-cabildo'),

    #---------------------- IMPORT -----------------------
    path('import', import_views.import_db, name='import'),
    path('import-db', import_views.import_db_file, name='import-db'),

    #---------------------- EMAIL -----------------------
    path('email-warning/<slug:token>/', views.email_warning, name='email-warning'),
    path('email-test', views.email_test, name='email-test'),

    #---------------------- AUTO -----------------------
    path('autosave_field/', auto_views.autosave_field, name='autosave_field'),
    path('autoremove_obj/', auto_views.autoremove_obj, name='autoremove_obj'),
]

