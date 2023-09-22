import os
os.environ["DJANGO_SETTINGS_MODULE"] = "project.maps.settings"
import django
from django.conf import settings
django.setup()
from .models import HasWaypoint, HasAuthor


def get_route_waypoints(route_id):
    if HasWaypoint.objects.filter(route=route_id).exists():
        ids_added = []
        waypoints = []
        rows = HasWaypoint.objects.raw("SELECT map.has_waypoint.route, map.waypoint.id, map.waypoint.name, map.waypoint.ascii_name, map.waypoint.lat, map.waypoint.lng, map.waypoint.country, map.waypoint.country_code, map.waypoint.description, map.waypoint.alternative_names, map.waypoint.roman_settlement_wp, wc.waypoint_type, hws.source, map.has_waypoint.wp_order  FROM map.has_waypoint JOIN map.waypoint ON map.has_waypoint.waypoint = map.waypoint.id LEFT JOIN map.waypoint_couple wc on map.waypoint.id = wc.waypoint LEFT JOIN map.waypoint_type wt on wt.id = wc.waypoint_type LEFT JOIN map.has_waypoint_source hws on wt.id = hws.waypoint_type WHERE has_waypoint.route = %s ORDER BY map.has_waypoint.wp_order", [route_id])
        for wp in rows:
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
                waypoints.append(wp_json)
                ids_added.append(wp.id)
            else:
                # Find wp
                wp_to_be_found = None
                list_indexes = [i for i, wp_i in enumerate(waypoints) if wp_i["id"] == wp.id]
                if len(list_indexes) > 0:
                    wp_index = list_indexes[0]
                    wp_to_be_found = waypoints[wp_index]
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
                                    # Are there other sources already? (1) Yes => check if the current source is missing and, if so, add it; (2) No => create the "sources" array and add the current source
                                    if "sources" in wpt:
                                        sources_list = list(map(lambda x: x["value"], wpt["sources"]))
                                        if wp.source not in sources_list:
                                            source_dict = {"id": len(sources_list) + 1, "value": wp.source}
                                            wpt["sources"].append(source_dict)
                                    else:
                                        wpt["sources"] = []
                                        source_dict = {"id": 1, "value": wp.source}
                                        wpt["sources"].append(source_dict)
        return waypoints

    return None


def getSourceAuthors(source_id):
    if HasAuthor.objects.filter(source=source_id).exists():
        authors = []
        rows = HasAuthor.objects.raw(
            "SELECT map.has_author.source, map.has_author.author FROM map.has_author WHERE has_author.source = %s ORDER BY map.has_author.author_order ASC",
            [source_id])
        for idx, has_author in enumerate(rows):
            wp_json = {"id": has_author.author.id, "name": has_author.author.name, "surname": has_author.author.surname, "rank": idx+1}
            authors.append(wp_json)
        return authors

    return None