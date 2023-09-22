import hashlib
import json
import os
import sys
import uuid

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .utils import get_route_waypoints, getSourceAuthors

workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the current path of your .py file
backend_path = os.path.join(workpath, '../../../backend')
sys.path.insert(0, backend_path)

# Create your views here.
from .models import User, Waypoint, WaypointType, Author, Source, WaypointCouple, HasWaypointSource, RouteType, \
    HasRouteSource, Route, RouteCouple, HasWaypoint, HasAuthor
from django.conf import settings


def index(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}

    return render(request, "index.html", context=context)


def index_login_required(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    username = None
    response = {"message": "An error occurred, not authorized", "messageType": "error"}

    if (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        response = {"username": username}
    elif "username" in request.session and request.session["username"] is not None:
        username = request.session["username"]
    if username is not None:
        print("username", username)
        return render(request, "index.html", context=context)

    print("username", username)
    return redirect("login")


def login(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "Credentials not valid!", "messageType": "error"}
    data = request.body
    print(str(data))
    if len(str(data).replace("b''", "")) > 0:
        data = json.loads(data)
        username = data.get("username", None)
        password = data.get("password", None)
        print(username, password)
        if username is not None and password is not None:
            # Try to validate
            if User.objects.filter(username=username,
                                   password=hashlib.md5(password.encode("utf-8")).hexdigest()).exists():
                print("User exists!")
                request.session["username"] = username
                response = {"username": username}
    else:
        return render(request, "index.html", context=context)
    return JsonResponse(response)


def logout(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}

    if "username" in request.session and request.session["username"] is not None:
        del request.session["username"]
    return redirect(settings.BASE_URL)


def get_current_user(request):
    response = {"message": "No user session found"}
    if (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        response = {"username": username}
    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
        response = {"username": username}
    return JsonResponse(response)


def user_info(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "No user session found!", "messageType": "error"}
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        # Try to validate and get other info
        if User.objects.filter(username=username).exists():
            userinfo = User.objects.filter(username=username).values('username', 'email', 'profile')
            userinfo = userinfo[0]
            print(userinfo)
            response = {"username": username, "email": userinfo["email"], "profile": userinfo["profile"]}
    else:
        return render(request, "index.html", context=context)
    return JsonResponse(response)


def get_all_waypoints(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)

    response = {"waypoints": []}

    query_result = Waypoint.objects.all().values('id', 'ascii_name', 'lat', 'lng', 'country')

    for wp in query_result:
        response["waypoints"].append(wp)

    return JsonResponse(response)


def search_waypoints(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)

    response = {"waypoints": []}

    data = request.body

    if len(str(data).replace("b''", "")) > 0:
        data = json.loads(data)
        query = data.get("query", None)
        print(query)
        ids_added = []
        if query is not None:
            loose_query = "%" + query + "%"
            # Try a loose match
            if len(Waypoint.objects.raw(
                    "SELECT map.waypoint.id, map.waypoint.name, map.waypoint.ascii_name, map.waypoint.lat, map.waypoint.lng, map.waypoint.country, map.waypoint.country_code, map.waypoint.description, map.waypoint.alternative_names, map.waypoint.roman_settlement_wp, map.waypoint_couple.waypoint_type, map.has_waypoint_source.source FROM map.waypoint LEFT JOIN map.waypoint_couple ON map.waypoint.id=map.waypoint_couple.waypoint LEFT JOIN map.has_waypoint_source ON map.has_waypoint_source.waypoint=map.waypoint.id AND map.has_waypoint_source.waypoint_type=map.waypoint_couple.waypoint_type  WHERE name ilike %s OR alternative_names ilike %s ORDER BY levenshtein_less_equal(map.waypoint.name::text, %s::text, 3) ASC",
                    [loose_query, loose_query, query])) > 0:
                query_result = Waypoint.objects.raw(
                    "SELECT map.waypoint.id, map.waypoint.name, map.waypoint.ascii_name, map.waypoint.lat, map.waypoint.lng, map.waypoint.country, map.waypoint.country_code, map.waypoint.description, map.waypoint.alternative_names, map.waypoint.roman_settlement_wp, map.waypoint_couple.waypoint_type, map.has_waypoint_source.source FROM map.waypoint LEFT JOIN map.waypoint_couple ON map.waypoint.id=map.waypoint_couple.waypoint LEFT JOIN map.has_waypoint_source ON map.has_waypoint_source.waypoint=map.waypoint.id AND map.has_waypoint_source.waypoint_type=map.waypoint_couple.waypoint_type  WHERE name ilike %s OR alternative_names ilike %s ORDER BY levenshtein_less_equal(map.waypoint.name::text, %s::text, 3) ASC",
                    [loose_query, loose_query, query])

                for wp in query_result:
                    wp_json = {"id": wp.id, "name": wp.name, "ascii_name": wp.ascii_name, "lat": wp.lat, "lng": wp.lng,
                               "country": wp.country, "country_code": wp.country_code, "description": wp.description,
                               "alternative_names": wp.alternative_names, "roman_settlement": wp.roman_settlement_wp}

                    if wp.id not in ids_added:
                        if wp.waypoint_type is not None:
                            wp_json["types"] = []
                            type_dict = {"id": 1, "value": wp.waypoint_type, "sources": []}
                            # Add source if available
                            if wp.source is not None:
                                source_dict = {"id": 1, "value": wp.source}
                                type_dict["sources"].append(source_dict)
                            wp_json["types"].append(type_dict)
                        response["waypoints"].append(wp_json)
                        ids_added.append(wp.id)
                    else:
                        # Find wp
                        wp_to_be_found = None
                        list_indexes = [i for i, wp_i in enumerate(response["waypoints"]) if wp_i["id"] == wp.id]
                        if len(list_indexes) > 0:
                            wp_index = list_indexes[0]
                            wp_to_be_found = response["waypoints"][wp_index]
                            if "types" in wp_to_be_found:
                                types_list = list(map(lambda x: x["value"], wp_to_be_found["types"]))
                                if wp.waypoint_type not in types_list:
                                    type_dict = {"id": len(types_list) + 1, "value": wp.waypoint_type, "sources": []}
                                    # Add source if available
                                    if wp.source is not None:
                                        source_dict = {"id": 1, "value": wp.source}
                                        type_dict["sources"].append(source_dict)
                                    # Add the missing type to the waypoint
                                    wp_to_be_found["types"].append(type_dict)
                                else:
                                    # waypoint type already present => add potential missing sources
                                    # Find type
                                    list_indexes_type = [i for i, wptype_i in enumerate(wp_to_be_found["types"]) if
                                                         wp.waypoint_type == wptype_i["value"]]
                                    if len(list_indexes_type) > 0:
                                        type_index = list_indexes_type[0]
                                        wpt = wp_to_be_found["types"][type_index]
                                        # Add source if available
                                        if wp.source is not None:
                                            source_dict = {"id": 1, "value": wp.source}
                                            # Are there other sources already?
                                            # (1) Yes => check if the current source is missing and, if so, add it
                                            if "sources" in wpt:
                                                sources_list = list(map(lambda x: x["value"], wpt["sources"]))
                                                if wp.source not in sources_list:
                                                    source_dict = {"id": len(sources_list) + 1, "value": wp.source}
                                                    wpt["sources"].append(source_dict)
                                            else:
                                                # (2) No => create the "sources" array and add the current source
                                                wpt["sources"] = []
                                                source_dict = {"id": 1, "value": wp.source}
                                                wpt["sources"].append(source_dict)

    return JsonResponse(response)


def get_all_routes(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    routes = []
    if len(Route.objects.all()) > 0:
        res = Route.objects.raw(
            "SELECT map.route.id, map.route.name, map.route.description, map.route_couple.route_type, map.has_route_source.source, map.route.creator FROM map.route LEFT JOIN map.route_couple ON route.id = route_couple.route LEFT JOIN map.has_route_source ON route.id = has_route_source.route AND route_couple.route_type=has_route_source.route_type ORDER BY map.route.id ASC")
        for route in res:
            print(route.id)
            if route.id not in [r["id"] for r in routes]:
                waypoints = get_route_waypoints(route.id)
                route_json = {"id": route.id, "name": route.name, "description": route.description,
                              "creator": route.creator.username, "types": [], "types-flat": [], "sources-flat": [], "waypoints": waypoints}
                routes.append(route_json)

        #   Populates types
        for route in res:
            idx = [i for i, r in enumerate(routes) if route.id == r["id"]][0] if len(
                [i for i, r in enumerate(routes) if route.id == r["id"]]) > 0 else None
            if idx is not None:
                route_types_list = [rt["value"] for rt in routes[idx]["types"]]
                if route.route_type not in route_types_list:
                    routes[idx]["types"].append({"id": len(route_types_list)+1, "value": route.route_type, "sources": []})
                if route.route_type not in routes[idx]["types-flat"]:
                    routes[idx]["types-flat"].append(route.route_type)

        #   Populates sources
        for route in res:
            idx = [i for i, r in enumerate(routes) if route.id == r["id"]][0] if len(
                [i for i, r in enumerate(routes) if route.id == r["id"]]) > 0 else None
            if idx is not None:
               idx_type = [i for i, t in enumerate(routes[idx]["types"]) if route.route_type == t["value"]][0] if len(
                [i for i, t in enumerate(routes[idx]["types"]) if route.route_type == t["value"]]) > 0 else None
               if idx_type is not None:
                    if route.source not in routes[idx]["sources-flat"]:
                        routes[idx]["sources-flat"].append(route.source)
                    route_type_sources_list = [s["value"] for s in routes[idx]["types"][idx_type]["sources"]]
                    if route.source not in route_type_sources_list:
                        routes[idx]["types"][idx_type]["sources"].append({"id": len(route_type_sources_list)+1, "value": route.source})
        routes.sort(key=lambda x: x["id"])
    print(routes)
    response = {"routes": routes, "messageType": "success"}
    return JsonResponse(response, status=get_response_status(response))


def get_response_status(response):
    if "messageType" in response and response["messageType"] == "success":
        return 200
    elif "messageType" in response and response["messageType"] == "error":
        return 401
    return 400


def edit_waypoint_details(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "An error occurred, your edits were not saved", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            print(data)
            wp_id = data.get("id", None)
            wp_desc = data.get("description", None)
            wp_alternative_names = data.get("alternative_names", None)
            wp_types = data.get("waypoint_types", None)
            wp_roman_settlement = data.get("roman_settlement", None)
            print(wp_id, wp_types)

            if wp_id is not None:
                if Waypoint.objects.filter(id=wp_id).exists():
                    wp = Waypoint.objects.get(id=wp_id)
                    wp.description = wp_desc
                    wp.alternative_names = wp_alternative_names
                    wp.roman_settlement_wp = wp_roman_settlement
                    wp.save()
                    # Delete former couples-sources
                    couples_sources = HasWaypointSource.objects.filter(waypoint=wp)
                    for couple in couples_sources:
                        couple.delete()
                    # Delete former wp-wpType couples
                    couples = WaypointCouple.objects.filter(waypoint=wp)
                    for couple in couples:
                        couple.delete()

                    for wp_type in wp_types:
                        type = wp_type["value"]
                        if type is not None:
                            wp_type_obj = WaypointType.objects.get(id=type)
                            if not WaypointCouple.objects.filter(waypoint=wp, waypoint_type=wp_type_obj).exists():
                                WaypointCouple.objects.create(waypoint=wp, waypoint_type=wp_type_obj)
                            if "sources" in wp_type:
                                wptype_sources = wp_type["sources"]
                                for wpt_source in wptype_sources:
                                    source_obj = Source.objects.get(id=wpt_source["value"])
                                    if not HasWaypointSource.objects.filter(waypoint=wp, source=source_obj,
                                                                            waypoint_type=wp_type_obj).exists():
                                        HasWaypointSource.objects.create(waypoint=wp, source=source_obj,
                                                                         waypoint_type=wp_type_obj)
                    response = {"message": "Waypoint successfully updated!", "messageType": "success"}
                else:
                    response = {"message": "An error occurred, the waypoint requested does not exists!",
                                "messageType": "error"}

                return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def get_all_waypoint_types_list(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)

    wp_types = list(WaypointType.objects.all().values('id', 'description'))
    response = {"waypoints-types": wp_types, "messageType": "success"}
    return JsonResponse(response, status=get_response_status(response))


def get_all_route_types_list(request):
    deploy_mode = settings.DEPLOY_MODE
    context = {"deploy_mode": deploy_mode}
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        wp_types = list(RouteType.objects.all().values('id', 'description'))
        response = {"route-types": wp_types, "messageType": "success"}
        return JsonResponse(response, status=get_response_status(response))
    return redirect("login")

def get_all_authors_list(request):
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)

    authors = list(Author.objects.all().values('id', 'name', 'surname', 'date_of_birth', 'place_of_birth'))
    authors.sort(key=lambda x: x["id"])
    print(authors)
    response = {"authors": authors, "messageType": "success"}
    return JsonResponse(response, status=get_response_status(response))


def get_all_sources_list(request):
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)

    sources = list(Source.objects.all().values('id', 'title', 'short_title', 'type', 'publisher', 'publication_date', 'archive', 'series', 'sub_series', 'link', 'doi', 'creator'))
    sources.sort(key=lambda x: x["id"])
    print(sources)
    for s in sources:
        s["authors"] = getSourceAuthors(s["id"])
    response = {"sources": sources, "messageType": "success"}
    return JsonResponse(response, status=get_response_status(response))



def add_author(request):
    data = request.body
    payload = None
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data)) > 0:
            print(data)
            payload = json.loads(data)
            author_name = str(payload["authorName"]).capitalize()
            author_surname = str(payload["authorSurname"]).capitalize()
            author_date_of_birth = None
            author_birthplace = None
            if str(payload["authorDateOfBirth"]).lower() != "invalid date":
                author_date_of_birth = str(payload["authorDateOfBirth"])
            if "authorBirthPlace" in payload:
                author_birthplace = str(payload["authorBirthPlace"]).capitalize()
            print(author_date_of_birth, author_birthplace)
            id = author_surname + "-" + author_name
            if author_date_of_birth and author_date_of_birth is not None and len(author_date_of_birth) > 0:
                id += "-" + str(author_date_of_birth)
            if author_birthplace and author_birthplace is not None and len(author_birthplace) > 0:
                id += "-" + str(author_birthplace)
            # id += str(uuid.uuid4())
            original_id = id
            counter = 0
            while Author.objects.filter(id=id).exists():
                counter += 1
                id = original_id + "-" + str(counter)
            res = Author.objects.create(id=id, name=author_name, surname=author_surname,
                                        date_of_birth=author_date_of_birth, place_of_birth=author_birthplace)
            if res:
                response = {"message": "Author successfully created", "messageType": "success", "authorId": id}
                return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def add_source(request):
    data = request.body
    payload = None
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data)) > 0:
            print(data)
            payload = json.loads(data)
            #  Primary fields
            authors = payload["authors"]
            print("authors: ", authors)
            type = str(payload["type"])
            title = str(payload["title"]).strip().capitalize()
            # Secondary fields
            shortTitle = payload.get("shortTitle", None)
            pubDate = payload.get("pubDate", None)
            archive = payload.get("archive", None)
            series = payload.get("series", None)
            subSeries = payload.get("subSeries", None)
            publisher = payload.get("publisher", None)
            link = payload.get("link", None)
            doi = payload.get("doi", None)
            if User.objects.filter(username=username).exists():
                creator = User.objects.get(username=username)
            print(payload)
            authors_string = ""
            authors.sort(key=lambda x: x["rank"])
            for idx, author in enumerate(authors):
                if idx < len(authors) - 1:
                    authors_string += author["value"].split("-")[0]+","
                else:
                    authors_string += author["value"].split("-")[0]

            # Create the source
            id = authors_string + "-" + title.strip().capitalize()
            original_id = id
            counter = 0
            while Source.objects.filter(id=id).exists():
                counter += 1
                id = original_id + "-" + str(counter)

            res = Source.objects.create(id=id, type=type,
                                        title=title, short_title=shortTitle, publication_date=pubDate, archive=archive,
                                        series=series, sub_series=subSeries, publisher=publisher, link=link, doi=doi,
                                        creator=creator)
            #  Create the "hasAuthor" entries (add the source's authors)
            for author in authors:
                source_obj = Source.objects.get(id=id)
                author_obj = Author.objects.get(id=author["value"])
                HasAuthor.objects.create(source=source_obj, author=author_obj)

            if res:
                response = {"message": "Source successfully created", "messageType": "success", "sourceId": id}
                return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def add_route(request):
    response = {"message": "An error occurred, your edits were not saved", "messageType": "error"}
    data = request.body
    username = None

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            print(data)
            route_id = data.get("name", None)
            route_name = data.get("name", None)
            route_description = data.get("description", None)
            route_types = data.get("types", None)
            route_wps = data.get("waypoints", None)
            route = None
            print(route_id, route_types, route_wps)

            if route_id is not None:
                if User.objects.filter(username=username).exists():
                    creator = User.objects.get(username=username)
                if not Route.objects.filter(id=route_id).exists():
                    Route.objects.create(id=route_id, name=route_name, description=route_description, creator=creator)
                else:
                    counter = 1
                    while Route.objects.filter(id=route_id + "-" + str(counter)).exists():
                        counter += 1
                    route_id += "-" + str(counter)
                    route_name += "-" + str(counter)
                    Route.objects.create(id=route_id, name=route_name, description=route_description, creator=creator)

                route = Route.objects.get(id=route_id)

                # Delete former couples-sources
                couples_sources = HasRouteSource.objects.filter(route=route_id)
                for couple in couples_sources:
                    couple.delete()
                # Delete former wp-wpType couples
                couples = RouteCouple.objects.filter(route=route_id)
                for couple in couples:
                    couple.delete()
                # Delete former routes-wps couples
                couples = HasWaypoint.objects.filter(route=route_id)
                for couple in couples:
                    couple.delete()

                # Save new route types and sources
                if route_types is not None:
                    for route_type in route_types:
                        type = route_type["value"]
                        if type is not None:
                            route_type_obj = RouteType.objects.get(id=type)
                            if route and (
                            not RouteCouple.objects.filter(route=route, route_type=route_type_obj).exists()):
                                RouteCouple.objects.create(route=route, route_type=route_type_obj)
                            if "sources" in route_type:
                                routetype_sources = route_type["sources"]
                                for routetype_source in routetype_sources:
                                    source_obj = Source.objects.get(id=routetype_source["value"])
                                    if not HasRouteSource.objects.filter(route=route, source=source_obj,
                                                                         route_type=route_type_obj).exists():
                                        HasRouteSource.objects.create(route=route, source=source_obj,
                                                                      route_type=route_type_obj)
                # Save waypoints
                if route_wps is not None and len(route_wps) > 0:
                    for ii, wp in enumerate(route_wps):
                        waypoint_obj = Waypoint.objects.get(id=wp["id"])
                        if route and (
                                not HasWaypoint.objects.filter(route=route, waypoint=waypoint_obj).exists()):
                            HasWaypoint.objects.create(route=route, waypoint=waypoint_obj, wp_order=ii+1)

                response = {"message": "Route successfully created!", "messageType": "success"}
                return JsonResponse(response, status=get_response_status(response))
    return redirect("login")



def edit_route(request):
    response = {"message": "An error occurred, your edits were not saved", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            print(data)
            route_id = data.get("route_id", None)
            route_name = data.get("name", None)
            route_description = data.get("description", None)
            route_types = data.get("types", None)
            route_wps = data.get("waypoints", None)
            route = None
            print(route_id, route_types, route_wps)

            if route_id is not None and route_name is not None and route_description is not None:
                # Get the route
                if Route.objects.filter(id=route_id).exists():
                    route = Route.objects.get(id=route_id)
                    #  Update route name
                    route.name = route_name
                    #  Update route description
                    route.description = route_description

                    # Delete former couples-sources
                    couples_sources = HasRouteSource.objects.filter(route=route_id)
                    for couple in couples_sources:
                        couple.delete()
                    # Delete former wp-wpType couples
                    couples = RouteCouple.objects.filter(route=route_id)
                    for couple in couples:
                        couple.delete()
                    # Delete former routes-wps couples
                    couples = HasWaypoint.objects.filter(route=route_id)
                    for couple in couples:
                        couple.delete()

                    # Save new route types and sources
                    if route_types is not None:
                        for route_type in route_types:
                            type = route_type["value"]
                            if type is not None:
                                route_type_obj = RouteType.objects.get(id=type)
                                if route and (
                                not RouteCouple.objects.filter(route=route, route_type=route_type_obj).exists()):
                                    RouteCouple.objects.create(route=route, route_type=route_type_obj)
                                if "sources" in route_type:
                                    routetype_sources = route_type["sources"]
                                    for routetype_source in routetype_sources:
                                        source_obj = Source.objects.get(id=routetype_source["value"])
                                        if not HasRouteSource.objects.filter(route=route, source=source_obj,
                                                                             route_type=route_type_obj).exists():
                                            HasRouteSource.objects.create(route=route, source=source_obj,
                                                                          route_type=route_type_obj)
                    # Save waypoints
                    if route_wps is not None and len(route_wps) > 0:
                        for ii, wp in enumerate(route_wps):
                            waypoint_obj = Waypoint.objects.get(id=wp["id"])
                            if route and (
                                    not HasWaypoint.objects.filter(route=route, waypoint=waypoint_obj).exists()):
                                HasWaypoint.objects.create(route=route, waypoint=waypoint_obj, wp_order=ii+1)

                    route.save()
                    response = {"message": "Route successfully updated!", "messageType": "success"}
                    return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def delete_route(request):
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            route_id = data.get("id", None)
            if route_id is not None and Route.objects.filter(id=route_id).exists():
                route = Route.objects.get(id=route_id)

                # Delete route-type-source
                if HasRouteSource.objects.filter(route=route).exists():
                    entries = HasRouteSource.objects.filter(route=route)
                    for e in entries:
                        e.delete()

                # Delete route-type couples
                if RouteCouple.objects.filter(route=route).exists():
                    couples = RouteCouple.objects.filter(route=route)
                    for c in couples:
                        c.delete()

                # Delete former routes-wps couples
                if HasWaypoint.objects.filter(route=route).exists():
                    couples = HasWaypoint.objects.filter(route=route_id)
                    for c in couples:
                        c.delete()

                if route.delete()[0] > 0:
                    response = {"message": "The requested route has been successfully deleted!",
                                "messageType": "success"}
                else:
                    response = {"message": "Error: The requested route was not deleted!", "messageType": "error"}
            else:
                response = {"message": "Error: The requested route does not exist!", "messageType": "error"}
            print(response)
            return JsonResponse(response, status=get_response_status(response))
    return redirect("login")



def delete_author(request):
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            author_id = data.get("id", None)
            if author_id is not None and Author.objects.filter(id=author_id).exists():
                author = Author.objects.get(id=author_id)
                if author.delete()[0] > 0:
                    response = {"message": "The requested author has been successfully deleted!",
                                "messageType": "success"}
                else:
                    response = {"message": "Error: The requested author was not deleted!", "messageType": "error"}
            else:
                response = {"message": "Error: The requested author does not exist!", "messageType": "error"}
            print(response)
            return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def delete_source(request):
    response = {"message": "An error occurred, not authorized", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            source_id = data.get("id", None)
            if source_id is not None and Source.objects.filter(id=source_id).exists():
                source = Source.objects.get(id=source_id)

                # Delete existing HasAuthor records
                if HasAuthor.objects.filter(source=source).exists():
                    res_set = HasAuthor.objects.filter(source=source)
                    for r in res_set:
                        if r is not None:
                            r.delete()

                try:
                    if source.delete()[0] > 0:
                        response = {"message": "The requested source has been successfully deleted!",
                                    "messageType": "success"}
                    else:
                        response = {"message": "Error: The requested source was not deleted!", "messageType": "error"}
                except Exception as e:
                    response = {"message": "Error: The requested source was not deleted! Error details: "+str(e), "messageType": "error"}

            else:
                response = {"message": "Error: The requested source does not exist!", "messageType": "error"}
            print(response)
            return JsonResponse(response, status=get_response_status(response))
    return redirect("login")



def edit_author(request):
    response = {"message": "An error occurred, your edits were not saved", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            print(data)
            author_id = data.get("author_id", None)
            author_name = data.get("name", None)
            author_surname = data.get("surname", None)
            author_birthplace = data.get("birthplace", None)
            author_birthdate = data.get("birthdate", None)
            author = None
            print(author_id, author_name, author_surname, author_birthplace, author_birthdate)

            if author_id is not None and author_name is not None and author_surname is not None:
                # Get the author
                if Author.objects.filter(id=author_id).exists():
                    author = Author.objects.get(id=author_id)

                    #  Update author name
                    author.name = author_name
                    #  Update author surname
                    author.surname = author_surname
                    #  Update author place_of_birth
                    author.place_of_birth = author_birthplace
                    #  Update author date_of_birth
                    author.date_of_birth = author_birthdate

                    # Save and update author info
                    author.save()
                    response = {"message": "Author successfully updated!", "messageType": "success"}
                    return JsonResponse(response, status=get_response_status(response))
    return redirect("login")


def edit_source(request):
    response = {"message": "An error occurred, your edits were not saved", "messageType": "error"}
    data = request.body

    if "username" in request.session and request.session["username"] is not None:
        # Get the username
        username = request.session["username"]
    elif (settings.DEPLOY_MODE == "DEV"):
        username = 'admin'
        print(username)
    if username is not None:
        if len(str(data).replace("b''", "")) > 0:
            data = json.loads(data)
            print(data)
            source_id = data.get("source_id", None)
            source_title = data.get("title", None)
            source_short_title = data.get("short_title", None)
            source_type = data.get("type", None)
            source_publication_date = data.get("publication_date", None)
            source_archive = data.get("archive", None)
            source_series = data.get("series", None)
            source_sub_series = data.get("sub_series", None)
            source_publisher = data.get("publisher", None)
            source_link = data.get("link", None)
            source_doi = data.get("doi", None)
            source_authors = data.get("authors", None)
            source = None
            print(source_id, source_title, source_short_title, source_type, source_publication_date, source_archive, source_series, source_sub_series, source_publisher, source_link, source_doi, source_authors)

            if source_id is not None and source_title is not None and source_short_title is not None:

                # Get the source
                if Source.objects.filter(id=source_id).exists():
                    source = Source.objects.get(id=source_id)

                    #  Update source title
                    source.title = source_title
                    #  Update source source_short_title
                    source.short_title = source_short_title
                    #  Update source source_type
                    source.type = source_type
                    #  Update source source_publication_date
                    source.publication_date = source_publication_date
                    #  Update source source_archive
                    source.archive = source_archive
                    #  Update source source_series
                    source.series = source_series
                    #  Update source source_sub_series
                    source.sub_series = source_sub_series
                    #  Update source source_publisher
                    source.publisher = source_publisher
                    #  Update source source_link
                    source.link = source_link
                    #  Update source source_doi
                    source.doi = source_doi

                    # Save and update source info
                    source.save()

                    # Update source source_authors
                    # Delete previous authors
                    if HasAuthor.objects.filter(source=source).exists():
                        res_set = HasAuthor.objects.filter(source=source)
                        for r in res_set:
                            r.delete()

                    # Insert new authors
                    for author in source_authors:
                        author_obj = Author.objects.get(id=author["id"])
                        if not HasAuthor.objects.filter(source=source, author=author_obj).exists():
                            HasAuthor.objects.create(author=author_obj, source=source, author_order=author["rank"])

                    response = {"message": "Source successfully updated!", "messageType": "success"}
                    return JsonResponse(response, status=get_response_status(response))
    return redirect("login")
