create user micollerc
    createdb
    replication;

comment on role micollerc is 'User for the MICOLL ERC project';

create database micoll_erc_map
    with owner micollerc;

comment on database micoll_erc_map is 'This is the main database for the MICOLL ERC project aiming to manage the data concerning the routes taken by salesmen and pilgrims in the period ranging from the XI and XVII centuries.';

\c micoll_erc_map;

create schema map;

comment on schema map is 'Main schema for the MICOLL ERC maps';

alter schema map owner to micollerc;

create type profile as enum ('admin', 'linguist', 'historian', 'legal historian', 'computer engineer', 'expert');

alter type profile owner to micollerc;

create type waypoint_type_enum as enum ('Postal waystation', 'Postal terminus', 'City', 'Port', 'River port', 'Toll gate', 'University', 'Fair');

alter type waypoint_type_enum owner to micollerc;

create type source_type as enum ('primary', 'secondary');

alter type source_type owner to micollerc;

create type route_type_enum as enum ('Waterway', 'Postal route', 'Pilgrim road', 'Trade route');

alter type route_type_enum owner to micollerc;

create table if not exists map."user"
(
    username          varchar(500) not null
        constraint user_pk
            primary key,
    password          varchar(500) not null,
    email             text,
    profile           profile,
    website           text,
    domainofexpertise text
);

alter table map."user"
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map."user" to micollerc;

create extension IF NOT EXISTS fuzzystrmatch;
create extension IF NOT EXISTS postgis;
create extension IF NOT EXISTS plpgsql;

create table if not exists map.waypoint
(
    id                      varchar(100) not null
        constraint waypoint_pk
            primary key,
    geonameref              text,
    whgref                  text,
    miduraref               text,
    description             text,
    creator                 varchar(500),
    status                  text,
    spatial_geometry        geometry,
    name                    text,
    ascii_name              text,
    lat                     numeric(8, 5),
    lng                     numeric(8, 5),
    timezone                text,
    geonames_last_edit_date date,
    country                 text,
    country_code            text,
    alternative_names       text,
    roman_settlement_wp     boolean
);

comment on table map.waypoint is 'it is the “fundamental unit” of any route, indeed two waypoints can make up a route (see the minimum cardinality of hasWType relationship). Each waypoint has a creator (i.e., a user which creates the waypoint and saves it in the database for the first time) and a status indicating whether the waypoint is just a draft or it has been confirmed by a user. A description for each waypoint is provided helping the user realize the nature of the waypoint. In addition, geospatial information about the waypoint are saved (see MiduraRef, GeonameRef, WHGRef). Each waypoint should have at least one type specified but can have multiple types (see the requirements section above) that are specified by means of the entity WaypointType.';

comment on column map.waypoint.roman_settlement_wp is 'This attribute says whether the waypoint (wp) was a roman settlement or not.';

alter table map.waypoint
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.waypoint to micollerc;

create table if not exists map.waypoint_type
(
    id          waypoint_type_enum not null
        constraint waypoint_type_pk
            primary key,
    description text
);

comment on table map.waypoint_type is 'represents the type of a waypoint, namely: Postal waystation, Postal terminus, City, Port, River port, Toll gate, University, Fair ';

alter table map.waypoint_type
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.waypoint_type to micollerc;

create table if not exists map.source
(
    id               varchar(500) not null
        constraint source_pk
            primary key,
    type             source_type,
    creator          varchar(500)
        constraint source_user__fk
            references map."user"
            on update cascade,
    status           text,
    title            text,
    short_title      text,
    publication_date date,
    archive          text,
    series           text,
    sub_series       text,
    publisher        text,
    link             text,
    doi              text
);

comment on table map.source is 'it is an historical source of evidence supporting the existence of routes and waypoints. It can be primary or secondary (mutually exclusive) this information is specified by the attribute type. Note that, for this reason, some attributes concern only primary sources (i.e., TBD) whereas others refer to secondary ones (i.e., TBD). The attributes representing a source include (if applicable): title, short title, publication date, archive, series, sub-series, publisher, link, DOI, author. In addition, each source has a creator (i.e., a user which creates the source and saves it in the database for the first time) and a status indicating whether the source is just a draft or it has been confirmed by a user. ';

alter table map.source
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.source to micollerc;

create table if not exists map.route
(
    id          varchar(500) not null
        constraint route_pk
            primary key,
    name        text not null,
    historical  boolean,
    description text,
    status      text,
    creator     varchar(500) not null
        constraint route_creator__fk
            references map."user"
            on update cascade
);

comment on table map.route is 'represents a route followed by pilgrims or salesmen to reach a specific destination (waypoint). Each route is made up at least of two waypoints and can be “historical” (i.e., based on historical evidence) or “conjectural” if it is just an hypothesis. Each route has a creator (i.e., a user which creates the route and saves it in the database for the first time) and a status indicating whether the route is just a draft or it has been confirmed by a user. Each route has a name and a description providing the user information about the route, so that it can be easily recognized. A route should have at least one type specified but can have multiple types (see the requirements section above) that are specified by means of the entity RouteType. ';

alter table map.route
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.route to micollerc;

create table if not exists map.route_type
(
    id          route_type_enum not null
        constraint route_type_pk
            primary key,
    description text
);

comment on table map.route_type is 'represents the type of a route, namely: Waterway, Postal route, Pilgrim road, Trade route ';

alter table map.route_type
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.route_type to micollerc;

create table if not exists map.has_waypoint_source
(
    waypoint      varchar(500)           not null
        constraint has_waypoint_source_waypoint_id_fk
            references map.waypoint
            on update cascade,
    source        varchar(500)           not null
        constraint has_waypoint_source_source_id_fk
            references map.source
            on update cascade,
    attestation   date,
    waypoint_type waypoint_type_enum not null
        constraint has_waypoint_source_waypoint_type_id_fk
            references map.waypoint_type
            on update cascade,
    constraint has_waypoint_source_pk
        primary key (waypoint, waypoint_type, source)
);

comment on table map.has_waypoint_source is 'keeps track of the Waypoint-Source links, that is, which sources are supporting a waypoint of interest. It saves the historical attestation of a route in a given source.';

alter table map.has_waypoint_source
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.has_waypoint_source to micollerc;

create table if not exists map.has_route_source
(
    route       varchar(500)        not null
        constraint has_route_source_route_id_fk
            references map.route
            on update cascade,
    source      varchar(500)        not null
        constraint has_route_source_source_id_fk
            references map.source
            on update cascade,
    attestation date,
    route_type  route_type_enum not null
        constraint has_route_source_route_type_id_fk
            references map.route_type
            on update cascade,
    constraint has_route_source_pk
        primary key (route, route_type, source)
);

comment on table map.has_route_source is 'keeps track of the Route-Source links, that is, which sources are supporting a route of interest. It saves the historical attestation of a route in a given source.';

alter table map.has_route_source
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.has_route_source to micollerc;

create table if not exists map.edit_route
(
    route             varchar(500) not null
        constraint edit_route_route_id_fk
            references map.route
            on update cascade,
    editor            varchar(500) not null
        constraint edit_route_user_username_fk
            references map."user"
            on update cascade,
    timestamp         timestamp    not null,
    edited_attributes json,
    id                serial
        constraint edit_route_pk
            primary key
);

alter table map.edit_route
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.edit_route to micollerc;

create table if not exists map.edit_waypoint
(
    "user"            varchar(500) not null
        constraint edit_waypoint_user_username_fk
            references map."user"
            on update cascade,
    waypoint          varchar(500) not null
        constraint edit_waypoint_waypoint_id_fk
            references map.waypoint
            on update cascade,
    timestamp         timestamp    not null,
    edited_attributes json,
    id                serial
        constraint edit_waypoint_pk
            primary key
);

comment on table map.edit_waypoint is 'keeps track of the updates and modifications of the attributes of a waypoint, carried out by a user. It includes a timestamp of the update event as well as a JSON serialization of the key-value pairs related to the updated attributes.';

alter table map.edit_waypoint
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.edit_waypoint to micollerc;

create table if not exists map.has_waypoint
(
    route      varchar(500) not null
        constraint has_waypoint_route_id_fk
            references map.route
            on update cascade,
    waypoint   varchar(500) not null
        constraint has_waypoint_waypoint_id_fk
            references map.waypoint
            on update cascade,
    historical boolean,
    wp_order   integer,
    constraint has_waypoint_pk
        primary key (route, waypoint)
);

comment on table map.has_waypoint is 'keeps track of the Route-Waypoint links, that is, which waypoints made up a route of interest. Moreover, It saves whether the waypoint is “historical” (i.e., based on historical evidence) or “conjectural” if it is just an hypothesis. ';

comment on column map.has_waypoint.wp_order is 'Specify the order of a waypoint in a given route';

alter table map.has_waypoint
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.has_waypoint to micollerc;

create table if not exists map.edit_source
(
    source            varchar(500) not null
        constraint edit_source_source_id_fk
            references map.source
            on update cascade,
    editor            varchar(500) not null
        constraint edit_source_user_username_fk
            references map."user"
            on update cascade,
    timestamp         timestamp    not null,
    edited_attributes json,
    id                serial
        constraint edit_source_pk
            primary key
);

comment on table map.edit_source is 'keeps track of the updates and modifications of the attributes of a source, carried out by a user. It includes a timestamp of the update event as well as a JSON serialization of the key-value pairs related to the updated attributes.';

alter table map.edit_source
    owner to micollerc;

grant delete, insert, references, select, trigger, truncate, update on map.edit_source to micollerc;

create table if not exists map.route_couple
(
    route      varchar             not null
        constraint route_couple_route_id_fk
            references map.route
            on update cascade,
    route_type route_type_enum not null
        constraint route_couple_route_type_id_fk
            references map.route_type
            on update cascade,
    historical boolean,
    constraint route_couple_pk
        primary key (route, route_type)
);

comment on table map.route_couple is 'indicates all the possible (multiple) different types of a given route.';

comment on column map.route_couple.historical is 'indicates whether a route and its type are historical (true) or conjectural (false)';

alter table map.route_couple
    owner to micollerc;

create table if not exists map.waypoint_couple
(
    waypoint      varchar                not null
        constraint waypoint_couple_waypoint_id_fk
            references map.waypoint
            on update cascade,
    waypoint_type waypoint_type_enum not null
        constraint waypoint_couple_waypoint_type_id_fk
            references map.waypoint_type
            on update cascade,
    historical    boolean,
    constraint waypoint_couple_pk
        primary key (waypoint, waypoint_type)
);

comment on table map.waypoint_couple is 'indicates all the possible (multiple) different types of a given waypoint.';

comment on column map.waypoint_couple.historical is 'indicates whether a waypoint and its type are historical (true) or conjectural (false)';

alter table map.waypoint_couple
    owner to micollerc;

create table if not exists map.author
(
    id             varchar not null
        constraint author_pk
            primary key,
    name           text,
    surname        text,
    date_of_birth  date,
    place_of_birth text
);

comment on table map.author is 'Author information, such as author name and surname.';

alter table map.author
    owner to micollerc;

create table if not exists map.has_author
(
    source       varchar(500) not null
        constraint has_author_source_id_fk
            references map.source
            on update cascade,
    author       varchar not null
        constraint has_author_author_id_fk
            references map.author
            on update cascade,
    author_order integer,
    constraint has_author_pk
        primary key (source, author)
);

comment on table map.has_author is 'This table indicates the authors for each source';

alter table map.has_author
    owner to micollerc;
