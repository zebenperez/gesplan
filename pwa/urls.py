from django.urls import path
from pwa import views, driver_views, driver_mpl_views, incidents_views, operator_views, actions_views, external_views


urlpatterns = [
    path('', views.index, name="pwa-home"),
    path('home/', views.index, name="pwa-home"),
    path('login/', views.pin_login, name="pwa-login"),
    path('logoff/', views.pin_logout, name="pwa-logout"),
    path('logoff-confirm/', views.pin_logout_confirm, name="pwa-logout-confirm"),
    path('access-log/', views.access_log, name="pwa-access-log"),
    path('select-truck', views.select_truck, name="pwa-select-truck"),
    path('save-truck', views.save_truck, name="pwa-save-truck"),
    path('set-km', views.set_km, name="pwa-set-km"),
    path('save-km', views.save_km, name="pwa-save-km"),


    # DRIVER
    path('driver/', driver_views.driver_home, name="pwa-driver"),

    path('driver/routes', driver_views.driver_routes, name="pwa-driver-routes"),
    path('driver/routes/source', driver_views.driver_routes_source, name="pwa-driver-routes-source"),
    path('driver/routes/waste', driver_views.driver_routes_waste, name="pwa-driver-routes-waste"),
    path('driver/routes/confirm', driver_views.driver_routes_confirm, name="pwa-driver-routes-confirm"),
    path('driver/routes/start/<int:source>/<int:waste>/<int:tray>/', driver_views.driver_routes_start, name="pwa-driver-routes-start"),
    path('driver/routes/target/<int:route>/', driver_views.driver_routes_target, name="pwa-driver-routes-target"),
    path('driver/routes/finish/', driver_views.driver_routes_finish, name="pwa-driver-routes-finish"),
    path('driver/routes/dir/<int:route_id>', driver_views.driver_routes_dir, name="pwa-driver-routes-dir"),

    path('driver/routes/source/exp/', driver_views.driver_routes_source_exp, name="pwa-driver-routes-source-exp"),
    path('driver/routes/start/exp/', driver_views.driver_routes_start_exp, name="pwa-driver-routes-start-exp"),
    path('driver/routes/target/exp/<int:route>/', driver_views.driver_routes_target_exp, name="pwa-driver-routes-target-exp"),

    #path('driver/actions/', driver_views.actions, name="pwa-driver-actions"),
    #path('driver/save-action/', driver_views.save_action, name="pwa-driver-save-action"),
    #path('driver/routes/end/<int:route>/', driver_views.driver_routes_end, name="pwa-driver-routes-end"),
    #path('driver/routes/end/<int:route>/<int:target>/', driver_views.driver_routes_end, name="pwa-driver-routes-end"),

    # DRIVER MPL
    path('driver-mpl/', driver_mpl_views.driver_home, name="pwa-driver-mpl"),
    path('driver-mpl/routes', driver_mpl_views.driver_routes, name="pwa-driver-mpl-routes"),
    path('driver-mpl/routes/source', driver_mpl_views.driver_routes_source, name="pwa-driver-mpl-routes-source"),
    path('driver-mpl/routes/waste', driver_mpl_views.driver_routes_wastes, name="pwa-driver-mpl-routes-wastes"),
    path('driver-mpl/routes/confirm', driver_mpl_views.driver_routes_confirm, name="pwa-driver-mpl-routes-confirm"),
    path('driver-mpl/routes/target/<int:route>/', driver_mpl_views.driver_routes_target, name="pwa-driver-mpl-routes-target"),
    path('driver-mpl/routes/finish/', driver_mpl_views.driver_routes_finish, name="pwa-driver-mpl-routes-finish"),
    path('driver-mpl/routes/end/<int:route>/', driver_mpl_views.driver_routes_end, name="pwa-driver-mpl-routes-end"),

    # INCIDENTS 
    path('incidents/incidents', incidents_views.incidents, name="pwa-incidents"),
    path('incidents/incidents/add', incidents_views.incidents_add, name="pwa-incidents-add"),
    path('incidents/incidents/save', incidents_views.incidents_save, name="pwa-incidents-save"),

    # OPERATOR
    path('operator/', operator_views.operator_home, name="pwa-operator"),
    path('operator/wastes/', operator_views.operator_wastes, name="pwa-operator-wastes"),
    path('operator/wastes/form/', operator_views.operator_wastes_form, name="pwa-operator-wastes-form"),
    path('operator/wastes/save/', operator_views.operator_wastes_save, name="pwa-operator-wastes-save"),
    path('operator/citizens/', operator_views.operator_citizens, name="pwa-operator-citizens"),
    path('operator/citizens/form/', operator_views.operator_citizens_form, name="pwa-operator-citizens-form"),
    path('operator/citizens/save/', operator_views.operator_citizens_save, name="pwa-operator-citizens-save"),
    path('operator/citizens/remove/<int:obj_id>', operator_views.operator_citizens_remove, name="pwa-operator-citizens-remove"),
    path('operator/citizens/waste/save/', operator_views.operator_citizens_waste_save, name="pwa-operator-citizens-waste-save"),
    path('operator/citizens/waste/force/', operator_views.operator_citizens_waste_force, name="pwa-operator-citizens-waste-force"),
    path('operator/citizens/waste/remove/', operator_views.operator_citizens_waste_remove, name="pwa-operator-citizens-waste-remove"),
    path('operator/facility/select/', operator_views.facility_select, name="pwa-operator-facility-select"),
    path('operator/facility/save/', operator_views.facility_save, name="pwa-operator-facility-save"),

    # EXTERNAL
    path('external/', external_views.external_home, name="pwa-external"),
    path('external/wastes/', external_views.external_wastes, name="pwa-external-wastes"),
    path('external/routes', external_views.external_routes, name="pwa-external-routes"),
    path('external/routes/form/', external_views.external_routes_form, name="pwa-external-routes-form"),
    path('external/routes/save/', external_views.external_routes_save, name="pwa-external-routes-save"),

    # ACTIONS
    path('actions/actions/', actions_views.actions, name="pwa-actions"),
    path('actions/save-action/', actions_views.save_action, name="pwa-actions-save"),


    #path('manager/', views.manager_home, name="pwa-manager"),

#    # OPERATOR
#    url(r'^operator/$', views.operator_home, name="pwa-operator"),
#    url(r'^operator/wastes/$', views.operator_wastes, name="pwa-operator-waste"),
#    url(r'^operator/wastes/save/$$', views.operator_waste_save, name="pwa-operator-waste-save"),
#    url(r'^operator/wastes/edit/(?P<waste_id>\d+)/$', views.operator_waste_edit, name="pwa-operator-waste-edit"),
#    url(r'^operator/wastes/edit/$', views.operator_waste_edit, name="pwa-operator-waste-edit"),
#
#    url(r'^operator/routes/$', views.operator_routes, name="pwa-operator-route"),
#    url(r'^operator/routes/check/(?P<route_id>\d+)/$', views.operator_route_check, name="pwa-operator-route-check"),
#
#    url(r'^operator/incidents/$', views.operator_incidents, name="pwa-operator-incidents"),
#    url(r'^operator/incidents/save/$$', views.operator_incident_save, name="pwa-operator-incident-save"),
#    url(r'^operator/incidents/edit/(?P<incident_id>\d+)/$', views.operator_incident_edit, name="pwa-operator-incident-edit"),
#    url(r'^operator/incidents/edit/$', views.operator_incident_edit, name="pwa-operator-incident-edit"),
#
#    url(r'^operator/citizens/$', views.operator_citizens, name="pwa-operator-citizens"),
#    url(r'^operator/citizens/save/$$', views.operator_citizen_save, name="pwa-operator-citizen-save"),
#    url(r'^operator/citizens/edit/(?P<citizen_id>\d+)/$', views.operator_citizen_edit, name="pwa-operator-citizen-edit"),
#    url(r'^operator/citizens/edit/$', views.operator_citizen_edit, name="pwa-operator-citizen-edit"),
#    url(r'^operator/citizens/remove/(?P<citizen_id>\d+)/$', views.operator_citizen_remove, name="pwa-operator-citizen-remove"),
#    url(r'^operator/citizens/waste/(?P<citizen_id>\d+)/$', views.operator_citizen_waste, name="pwa-operator-citizen-waste"),
#    url(r'^operator/citizens/waste/(?P<citizen_id>\d+)/(?P<waste_id>\d+)/(?P<units>\d+.\d+)/(?P<msg>.*)/$', views.operator_citizen_waste, name="pwa-operator-citizen-waste"),
#    url(r'^operator/citizens/waste/save/$$', views.operator_citizen_waste_save, name="pwa-operator-citizen-waste-save"),
#    url(r'^operator/citizens/waste/remove/(?P<citizen_id>\d+)/$', views.operator_citizen_waste_remove, name="pwa-operator-citizen-waste-remove"),
#    url(r'^operator/citizens/waste/end/(?P<citizen_id>\d+)/$', views.operator_citizen_waste_end, name="pwa-operator-citizen-end"),
#
#    url(r'^operator/citizens/sessions/$', views.operator_sessions, name="pwa-operator-sessions"),
#    url(r'^operator/citizens/ini-workday/$', views.operator_ini_workday, name="pwa-operator-ini-workday"),
#    url(r'^operator/citizens/end-workday/$', views.operator_end_workday, name="pwa-operator-end-workday"),
#
#
#    url(r'^driver/incidents/$', views.driver_incidents, name="pwa-driver-incidents"),
#    url(r'^driver/incidents/save/$$', views.driver_incident_save, name="pwa-driver-incident-save"),
#    url(r'^driver/incidents/edit/(?P<incident_id>\d+)/$', views.driver_incident_edit, name="pwa-driver-incident-edit"),
#    url(r'^driver/incidents/edit/$', views.driver_incident_edit, name="pwa-driver-incident-edit"),
#
#    url(r'^driver/trays/$', views.driver_trays, name="pwa-driver-trays"),
#    #url(r'^driver/trays/save/$$', views.driver_tray_save, name="pwa-driver-tray-save"),
#    #url(r'^driver/trays/edit/(?P<tray_id>\d+)/$', views.driver_tray_edit, name="pwa-driver-tray-edit"),
#    #url(r'^driver/trays/edit/$', views.driver_tray_edit, name="pwa-driver-tray-edit"),
#
#    url(r'^driver/routes/$', views.driver_routes, name="pwa-driver-routes"),
#    url(r'^driver/routes/view/(?P<route_id>\d+)/$', views.driver_route_view, name="pwa-driver-route-view"),
#    url(r'^driver/routes/ini/$', views.driver_ini_route, name="pwa-driver-ini-route"),
#    url(r'^driver/routes/end/$', views.driver_end_route, name="pwa-driver-end-route"),
#    url(r'^driver/routes/check-point/(?P<point_id>\d+)/$', views.driver_check_point, name="pwa-driver-check-point"),
#    url(r'^driver/routes/weight/save/$', views.driver_minipoint_weight_save, name="pwa-minipuntos-weight-save"),
#    url(r'^driver/routes/update-amount/$', views.driver_update_amount, name="pwa-driver-update-amount"),
#    url(r'^driver/routes/view-doc/(?P<point_id>\d+)/$', views.driver_view_doc, name="pwa-driver-view-doc"),
#
#    url(r'^driver/exp/$', views.driver_exp, name="pwa-driver-exp"),
#    url(r'^driver/exp/wif/save/$$', views.driver_wif_save, name="pwa-driver-wif-save"),
#    url(r'^driver/exp/wif/edit/(?P<waste_id>\d+)/$', views.driver_wif_edit, name="pwa-driver-wif-edit"),
#
#    url(r'^driver/routes/manage/$', views.driver_manage_routes, name="pwa-driver-manage-routes"),
#
#    # TEST
#    url(r'^test/save/$', views.storage_save, name="pwa-test-save"),
#    url(r'^test/load/$', views.storage_load, name="pwa-test-load"),
#    url(r'^test/reset/$', views.storage_reset, name="pwa-test-reset"),
]

