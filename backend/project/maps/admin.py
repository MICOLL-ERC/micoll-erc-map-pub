from django.contrib import admin
from .models import User, Waypoint, Route, RouteCouple, HasWaypoint, HasAuthor, HasWaypointSource, HasRouteSource, Author, WaypointCouple, WaypointType, EditWaypoint, EditRoute, EditSource

# Register your models here.
admin.site.register(User)
admin.site.register(Waypoint)
admin.site.register(Route)
admin.site.register(RouteCouple)
admin.site.register(HasWaypoint)
admin.site.register(HasAuthor)
admin.site.register(HasWaypointSource)
admin.site.register(HasRouteSource)
admin.site.register(WaypointCouple)
admin.site.register(WaypointType)
admin.site.register(EditWaypoint)
admin.site.register(EditRoute)
admin.site.register(EditSource)
admin.site.register(Author)