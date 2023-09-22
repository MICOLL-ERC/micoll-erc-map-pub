from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('new-author', views.index_login_required, name='index_login_required'),
    path('new-source', views.index_login_required, name='index_login_required'),
    path('new-route', views.index_login_required, name='index_login_required'),
    path('edit-waypoint', views.index_login_required, name='index_login_required'),
    path('user-profile', views.index_login_required, name='index_login_required'),
    path('manage-routes', views.index, name='index'),
    path('manage-authors', views.index, name='index'),
    path('manage-sources', views.index, name='index'),
    path('manage-waypoints', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('current-user', views.get_current_user, name='get_current_user'),
    path('user-info', views.user_info, name='user_info'),
    path('list-waypoints', views.get_all_waypoints, name='get_all_waypoints'),
    path('list-routes', views.get_all_routes, name='get_all_routes'),
    path('list-authors', views.get_all_authors_list, name='get_all_authors_list'),
    path('list-sources', views.get_all_sources_list, name='get_all_sources_list'),
    path('search-waypoints', views.search_waypoints, name='search_waypoints'),
    path('waypoint-types', views.get_all_waypoint_types_list, name='get_all_waypoint_types_list'),
    path('route-types', views.get_all_route_types_list, name='get_all_route_types_list'),
    path('authors', views.get_all_authors_list, name='get_all_authors_list'),
    path('sources', views.get_all_sources_list, name='get_all_sources_list'),
    path('add-author', views.add_author, name='add_author'),
    path('add-source', views.add_source, name='add_source'),
    path('add-route', views.add_route, name='add_route'),
    path('delete-route', views.delete_route, name='delete_route'),
    path('delete-author', views.delete_author, name='delete_author'),
    path('delete-source', views.delete_source, name='delete_source'),
    path('edit-route', views.edit_route, name='edit_route'),
    path('edit-author', views.edit_author, name='edit_author'),
    path('edit-source', views.edit_source, name='edit_source'),
    path('edit-waypoint-details', views.edit_waypoint_details, name='edit_waypoint_details'),
]
