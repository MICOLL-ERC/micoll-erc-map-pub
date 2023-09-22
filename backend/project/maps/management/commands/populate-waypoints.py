from django.core.management.base import BaseCommand, CommandError
from maps.models import Waypoint
import os
import pandas as pd
from tqdm import tqdm

class Command(BaseCommand):
    help = "Populate the waypoints in the database"

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        path = options["path"]

        if os.path.exists(path):
            self.stdout.write(
            self.style.SUCCESS('File path: "%s" exists!' % path))

            df = pd.read_csv(path, delimiter=";")

            for index, row in tqdm(df.iterrows()):
                geonameid = row['Geoname ID']
                name = row['Name']
                asciiname = row['ASCII Name']
                alternative_names = row['Alternate Names']
                latitude = row['Latitude']
                longitude = row['Longitude']
                country = row['Country']
                timezone = row['Timezone']
                modificationdate = row['Modification date']
                country_code = row["Country Code"]
                Waypoint.objects.create(id="geonames-"+str(geonameid), geonameref=geonameid, creator="admin", status="confirmed", name=name, ascii_name=asciiname, lat=latitude, lng=longitude, timezone=timezone, geonames_last_edit_date=modificationdate, country=country, alternative_names=alternative_names, country_code=country_code)
        else:
            self.stdout.write(
            self.style.ERROR('File path: "%s" does NOT exist!' % path))
