from django.db import models

# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class EditRoute(models.Model):
    route = models.ForeignKey('Route', models.DO_NOTHING, db_column='route')
    editor = models.ForeignKey('User', models.DO_NOTHING, db_column='editor')
    timestamp = models.DateTimeField(db_column='timestamp')
    edited_attributes = models.JSONField(db_column='edited_attributes', blank=True, null=True)
    id = models.IntegerField(db_column='id', primary_key=True)

    class Meta:
        managed = False
        db_table = 'edit_route'


class EditSource(models.Model):
    source = models.ForeignKey('Source', models.DO_NOTHING, db_column='source')
    editor = models.ForeignKey('User', models.DO_NOTHING, db_column='editor')
    timestamp = models.DateTimeField(db_column='timestamp')
    edited_attributes = models.JSONField(db_column='edited_attributes', blank=True, null=True)
    id = models.IntegerField(db_column='id', primary_key=True)

    class Meta:
        managed = False
        db_table = 'edit_source'
        db_table_comment = 'keeps track of the updates and modifications of the attributes of a source, carried out by a user. It includes a timestamp of the update event as well as a JSON serialization of the key-value pairs related to the updated attributes.'


class EditWaypoint(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='user')
    waypoint = models.ForeignKey('Waypoint', models.DO_NOTHING, db_column='waypoint')
    timestamp = models.DateTimeField(db_column='timestamp')
    edited_attributes = models.JSONField(db_column='edited_attributes', blank=True, null=True)
    id = models.IntegerField(db_column='id', primary_key=True)

    class Meta:
        managed = False
        db_table = 'edit_waypoint'
        db_table_comment = 'keeps track of the updates and modifications of the attributes of a waypoint, carried out by a user. It includes a timestamp of the update event as well as a JSON serialization of the key-value pairs related to the updated attributes.'


class HasRouteSource(models.Model):
    route = models.ForeignKey('Route', models.DO_NOTHING, db_column='route', primary_key=True)
    source = models.ForeignKey('Source', models.DO_NOTHING, db_column='source')
    route_type = models.ForeignKey('RouteType', models.DO_NOTHING, db_column='route_type')
    attestation = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'has_route_source'
        unique_together = (('route', 'route_type', 'source'),)
        db_table_comment = 'keeps track of the Route-Source links, that is, which sources are supporting a route of interest. It saves the historical attestation of a route in a given source.'


class RouteCouple(models.Model):
    route = models.ForeignKey('Route', models.DO_NOTHING, db_column='route', primary_key=True)
    route_type = models.ForeignKey('RouteType', models.DO_NOTHING, db_column='route_type')
    historical = models.BooleanField(db_column='historical', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_couple'
        unique_together = (('route', 'route_type'),)
        db_table_comment = 'indicates all the possible (multiple) different types of a given route.'


class HasWaypoint(models.Model):
    route = models.OneToOneField('Route', models.DO_NOTHING, db_column='route', primary_key=True)  # The composite primary key (route, waypoint) found, that is not supported. The first column is selected.
    waypoint = models.ForeignKey('Waypoint', models.DO_NOTHING, db_column='waypoint')
    historical = models.BooleanField(blank=True, null=True, db_column='historical')
    wp_order = models.IntegerField(blank=True, null=True, db_column='wp_order')

    class Meta:
        managed = False
        db_table = 'has_waypoint'
        unique_together = (('route', 'waypoint'),)
        db_table_comment = 'keeps track of the Route-Waypoint links, that is, which waypoints made up a route of interest. Moreover, It saves whether the waypoint is “historical” (i.e., based on historical evidence) or “conjectural” if it is just an hypothesis. '


class HasWaypointSource(models.Model):
    waypoint = models.ForeignKey('Waypoint', models.DO_NOTHING, db_column='waypoint', primary_key=True)
    source = models.ForeignKey('Source', models.DO_NOTHING, db_column='source')
    attestation = models.DateField(blank=True, null=True)
    waypoint_type = models.ForeignKey('WaypointType', models.DO_NOTHING, db_column='waypoint_type')

    class Meta:
        managed = False
        db_table = 'has_waypoint_source'
        unique_together = (('waypoint', 'waypoint_type', 'source'),)
        db_table_comment = 'keeps track of the Waypoint-Source links, that is, which sources are supporting a waypoint of interest. It saves the historical attestation of a route in a given source.'



class HasAuthor(models.Model):
    author = models.ForeignKey('Author', models.DO_NOTHING, db_column='author', primary_key=True)
    source = models.ForeignKey('Source', models.DO_NOTHING, db_column='source')
    author_order = models.IntegerField(db_column='author_order')

    class Meta:
        managed = False
        db_table = 'has_author'
        unique_together = (('author', 'source'),)
        db_table_comment = 'This table indicates the authors for each source'

class WaypointCouple(models.Model):
    waypoint = models.ForeignKey('Waypoint', models.DO_NOTHING, db_column='waypoint', primary_key=True)
    waypoint_type = models.ForeignKey('WaypointType', models.DO_NOTHING, db_column='waypoint_type')
    historical = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'waypoint_couple'
        unique_together = (('waypoint', 'waypoint_type'),)
        db_table_comment = 'indicates all the possible (multiple) different types of a given waypoint.'


class Route(models.Model):
    id = models.CharField(primary_key=True, max_length=500)
    name = models.TextField()
    historical = models.BooleanField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    creator = models.ForeignKey('User', models.DO_NOTHING, db_column='creator')

    class Meta:
        managed = False
        db_table = 'route'
        db_table_comment = 'represents a route followed by pilgrims or salesmen to reach a specific destination (waypoint). Each route is made up at least of two waypoints and can be “historical” (i.e., based on historical evidence) or “conjectural” if it is just an hypothesis. Each route has a creator (i.e., a user which creates the route and saves it in the database for the first time) and a status indicating whether the route is just a draft or it has been confirmed by a user. Each route has a name and a description providing the user information about the route, so that it can be easily recognized. A route should have at least one type specified but can have multiple types (see the requirements section above) that are specified by means of the entity RouteType. '


class RouteType(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_type'
        db_table_comment = 'represents the type of a route, namely: Waterway, Postal route, Pilgrim road, Trade route '


class Source(models.Model):
    id = models.CharField(primary_key=True, max_length=500)
    type = models.TextField(blank=True, null=True)  # This field type is a guess.
    creator = models.ForeignKey('User', models.DO_NOTHING, db_column='creator', blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    short_title = models.TextField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    archive = models.TextField(blank=True, null=True)
    series = models.TextField(blank=True, null=True)
    sub_series = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    doi = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'source'
        db_table_comment = 'it is an historical source of evidence supporting the existence of routes and waypoints. It can be primary or secondary (mutually exclusive) this information is specified by the attribute type. Note that, for this reason, some attributes concern only primary sources (i.e., TBD) whereas others refer to secondary ones (i.e., TBD). The attributes representing a source include (if applicable): title, short title, publication date, archive, series, sub-series, publisher, link, DOI, author. In addition, each source has a creator (i.e., a user which creates the source and saves it in the database for the first time) and a status indicating whether the source is just a draft or it has been confirmed by a user. '


class User(models.Model):
    username = models.CharField(primary_key=True, max_length=500)
    password = models.CharField(max_length=500)
    email = models.TextField(blank=True, null=True)
    profile = models.TextField(blank=True, null=True)  # This field type is a guess.
    website = models.TextField(blank=True, null=True)
    domainofexpertise = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Waypoint(models.Model):
    id = models.CharField(primary_key=True, max_length=500)
    geonameref = models.TextField(blank=True, null=True)
    whgref = models.TextField(blank=True, null=True)
    miduraref = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creator = models.CharField(max_length=500, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    spatial_geometry = models.TextField(blank=True, null=True)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    ascii_name = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    lng = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    timezone = models.TextField(blank=True, null=True)
    geonames_last_edit_date = models.DateField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    alternative_names = models.TextField(blank=True, null=True)
    roman_settlement_wp = models.BooleanField(blank=True, null=True, db_column="roman_settlement_wp")

    class Meta:
        managed = False
        db_table = 'waypoint'
        db_table_comment = 'it is the “fundamental unit” of any route, indeed two waypoints can make up a route (see the minimum cardinality of hasWType relationship). Each waypoint has a creator (i.e., a user which creates the waypoint and saves it in the database for the first time) and a status indicating whether the waypoint is just a draft or it has been confirmed by a user. A description for each waypoint is provided helping the user realize the nature of the waypoint. In addition, geospatial information about the waypoint are saved (see MiduraRef, GeonameRef, WHGRef). Each waypoint should have at least one type specified but can have multiple types (see the requirements section above) that are specified by means of the entity WaypointType.'


class Author(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    surname = models.TextField()
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'author'
        db_table_comment = 'Author information, such as author name and surname.'


class WaypointType(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'waypoint_type'
        db_table_comment = 'represents the type of a waypoint, namely: Postal waystation, Postal terminus, City, Port, River port, Toll gate, University, Fair '

