import argparse
import datetime
import getpass
import json
import logging
import re
import sys

import geojson
import geopandas as gpd
import pandas as pd
import requests
from dateutil.relativedelta import *
from tabulate import tabulate

# Set a custom log formatter
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Origin": "https://happywhale.com",
    "Referer": "https://happywhale.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def auth():
    json_data = {
        "username": "roysam@hawaii.edu",
        "password": "ydg9bpd3AGD9zmy.fdq",
        "rememberMe": True,
    }

    response = requests.post(
        "https://critterspot.happywhale.com/v1/core/user/login",
        headers=headers,
        json=json_data,
    )
    print(json.dumos(response.json()))


# auth()


def species_config():
    response = requests.get(
        "https://critterspot.happywhale.com/v1/cs/encounter/config", headers=headers
    )
    if response.status_code == 200:
        species_code = [
            [item.get("name"), item.get("code")] for item in response.json()["species"]
        ]
        if len(species_code) > 0:
            print("\n" + "================Species Name: Species Code================")
            print(
                "\n".join(
                    [" : ".join([str(cell) for cell in row]) for row in species_code]
                )
            )
        return species_code
    else:
        logging.error(
            f"Failed to get species config with error code: {response.status_code}"
        )


def species_from_parser(args):
    species_config()


def stats(stat_type):
    response = requests.get(
        "https://critterspot.happywhale.com/v1/cs/main/sitestats", headers=headers
    )
    if response.status_code == 200:
        # total photos
        total_photos = response.json()["site"]["numPhotos"]
        # user stats
        total_users = response.json()["site"]["users"]["num"]
        top_contributors = response.json()["site"]["users"]["topContribs"]
        top_contributors_year = response.json()["site"]["users"]["topContribsLastYear"]

        # encounter stats
        encounters_total = response.json()["site"]["encounters"]["num"]
        encounters_total_ided = response.json()["site"]["encounters"]["numIded"]
        encounters_recent = response.json()["site"]["encounters"]["mostRecent"]
        encounters_recent_ided = response.json()["site"]["encounters"]["mostRecentIded"]
        encounters_species = response.json()["site"]["encounters"]["bySpecies"]

        # individuals stats
        individuals_total = response.json()["site"]["individuals"]["num"]
        furthest_sighted = response.json()["site"]["individuals"]["furthestSighted"]
        longest_time_between = response.json()["site"]["individuals"][
            "longestTimeBetween"
        ]
        longest_first_last = response.json()["site"]["individuals"]["longestFirstLast"]
        most_sighted = response.json()["site"]["individuals"]["mostSighted"]

        ############### Print stats ###############
        logging.info(f"Total photos: {total_photos:,}")
        logging.info(f"Total users: {total_users:,}")
        logging.info(f"Total encounters {encounters_total:,}")
        logging.info(f"Total encounters ided: {encounters_total_ided:,}")
        logging.info(f"Encountered species: {len(encounters_species):,}")
        logging.info(f"Individuals total: {individuals_total}")
        if stat_type == "user" or stat_type == "users":
            print(
                "\n"
                + f"Now fetching total of {len(top_contributors):,} top contributors"
            )
            # top_contributors['user'])
            user_code = [
                [
                    item["user"].get("displayName"),
                    item.get("numEncs"),
                    item.get("numPhotos"),
                    item.get("rank"),
                ]
                for item in top_contributors
            ]
            if len(user_code) > 0:
                print("\n" + "================Top 10 Current Users================")
                for user in user_code:
                    display_name = re.sub(
                        r"\b\w", lambda x: x.group(0).upper(), user[0].lower()
                    )
                    print(
                        f"User/Org {display_name} with rank {user[3]}: Total enncounters {user[1]:,} and {user[2]:,} photos"
                    )
        if stat_type == "individuals" or stat_type == "individual":
            print(
                "\n"
                + f"Now fetching total of {len(most_sighted):,} most sighted individuals"
            )
            user_code = [
                [
                    item["individual"].get("nickname"),
                    item["individual"].get("species"),
                    item["individual"].get("sex"),
                    item.get("stat"),
                ]
                for item in most_sighted
            ]
            if len(user_code) > 0:
                print(
                    "\n"
                    + "================Most Sighted Individuals Stats================"
                )
                for user in user_code:
                    display_name = re.sub(
                        r"\b\w", lambda x: x.group(0).upper(), user[0].lower()
                    )
                    print(
                        f"{user[1]} with nickname {display_name} with {user[3]}: Total enncounters"
                    )
        if stat_type == "encounters" or stat_type == "encounter":
            print(
                "\n" + f"Now fetching total of {len(encounters_recent_ided)} encounters"
            )
            user_code = [
                [
                    item["encounter"]["species"],
                    item["encounter"]["region"],
                    item["encounter"]["dateRange"]["startDate"],
                    item["encounter"]["id"],
                ]
                for item in encounters_recent_ided
            ]
            if len(user_code) > 0:
                print("\n" + "================Most Recent Encounters================")
                for user in user_code:
                    print(
                        f"Encountered {user[0]} with encounter id {user[3]} in the {user[1]} region, on {user[2]}"
                    )


def stats_from_parser(args):
    stats(stat_type=args.st)


def id_fetch(id):
    response = requests.get(
        f"https://critterspot.happywhale.com/v1/cs/encounter/full/{id}", headers=headers
    )
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(
            f"Request failed with {response.status_code} and error message {response.text}"
        )


def fetch_from_parser(args):
    id_fetch(id=args.id)


def search():
    json_data = {
        "encounter": {
            "datesearch": {
                "preset": 2,
                "type": 4,
                "startdate": "2010-10-01",
                "enddate": "2023-11-01",
            },
            "species": "humpback_whale",
        },
        "showConnections": False,
    }

    response = requests.post(
        "https://critterspot.happywhale.com/v1/cs/admin/encounter/search",
        headers=headers,
        json=json_data,
    )
    print(len(response.json()))
    print(response.status_code)

    # for item in response.json():
    #     print(item)


# search()


def geom2bounds(geom):
    # Load the GeoJSON file
    geometry_file = geom
    gdf = gpd.read_file(geometry_file)
    locsearch = {
        "type": "mapbounds",
        "watergeo": None,
        "mapBounds": {
            "southWest": {
                "lat": gdf.bounds.miny.min(),
                "lng": gdf.bounds.minx.min(),
            },
            "northEast": {
                "lat": gdf.bounds.maxy.max(),
                "lng": gdf.bounds.maxx.max(),
            },
        },
    }
    return locsearch


def epoch_start(iso_date):
    date_obj = datetime.datetime.fromisoformat(iso_date)
    timestamp = int(date_obj.timestamp() * 1000)
    return timestamp


def species_match(list_of_dicts, search_string):
    for dictionary in list_of_dicts:
        for key, value in dictionary.items():
            if search_string in key:
                return value
            elif search_string in str(
                value
            ):  # Check if the search_string is in the value
                return value
    return None  # Return None if no match is found


def geometry_search(geometry_file, start, end, export, species):
    species_list = requests.get(
        "https://critterspot.happywhale.com/v1/cs/encounter/config", headers=headers
    )
    if species_list.status_code == 200:
        species_code = [
            {item.get("name"): item.get("code")}
            for item in species_list.json()["species"]
        ]
    species_val = species_match(species_code, species)
    if species_val is not None:
        species = species_val
    else:
        logging.error("Species not found choose from " + "\n")
        for species in species_code:
            for key, value in species.items():
                print(f"{value}")
        sys.exit()
    features = []  # to get the features from the search results
    flattened_data = []  # to create a flat list of features
    if start and end is not None:
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
    elif start is None and end is not None:
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        start = end + relativedelta(months=-1)
    elif start is not None and end is None:
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = start + relativedelta(months=1)
    elif start is None and end is None:
        end = datetime.datetime.utcnow()
        start = end + relativedelta(months=-1)
    logging.info(f"Searching between Start date {start} and End date {end}")
    json_data = {
        "showConnections": False,
        "encounter": {
            "species": species,
            "locsearch": {
                "type": "mapbounds",
                "watergeo": None,
                "mapBounds": {
                    "southWest": {
                        "lat": -90,
                        "lng": -180,
                    },
                    "northEast": {
                        "lat": 90,
                        "lng": 180,
                    },
                },
            },
            "datesearch": {
                "type": 3,
                "startdate": str(start).split(" ")[0],
                "enddate": str(end).split(" ")[0],
            },
        },
    }
    if geometry_file is None:
        logging.info(f"No geometry file specified using a global bounding box")
        # json_data['encounter'].pop('locsearch')
    else:
        loc_search = geom2bounds(geometry_file)
        json_data["encounter"]["locsearch"] = loc_search
    response = requests.post(
        "https://critterspot.happywhale.com/v1/cs/admin/encounter/search",
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        try:
            logging.info(f"Found a total of {len(response.json())} encounters")
            for i, json_obj in enumerate(response.json()):
                try:
                    # Extract location and other properties
                    location = json_obj["location"]
                    properties = {k: v for k, v in json_obj.items() if k != "location"}
                    # properties["displayImg"] = properties.pop("displayImage")
                    properties["system:time_start"] = epoch_start(
                        properties["dateRange"]["startDate"]
                    )
                    # Create a Feature
                    feature = geojson.Feature(
                        geometry=geojson.Point((location["lng"], location["lat"])),
                        properties=properties,
                    )
                    features.append(feature)
                except Exception as e:
                    logging.error(f"Subscription error for feature {i}: {e}")
                    continue
            feature_collection = geojson.FeatureCollection(features)
            geojson_data = geojson.dumps(feature_collection, sort_keys=True, indent=2)
            # print(geojson_data)
            if export.endswith("geojson"):
                with open(export, "w") as geojson_file:
                    geojson_file.write(geojson_data)
                logging.info(f"Search results exported to {export}")
            elif export.endswith("csv"):
                for i, feature in enumerate(
                    json.loads(geojson_data).get("features", [])
                ):
                    try:
                        flattened_feature = {
                            "latitude": feature["geometry"]["coordinates"][1],
                            "longitude": feature["geometry"]["coordinates"][0],
                            "approved": feature["properties"]["approved"],
                            "attrs": feature.get("properties", {}).get("attrs"),
                            "startDate": feature.get("properties", {})
                            .get("dateRange", {})
                            .get("startDate"),
                            "startTime": feature.get("properties", {})
                            .get("dateRange", {})
                            .get("startTime"),
                            "endDate": feature.get("properties", {})
                            .get("dateRange", {})
                            .get("endDate"),
                            "endTime": feature.get("properties", {})
                            .get("dateRange", {})
                            .get("endTime"),
                            "timezone": feature.get("properties", {})
                            .get("dateRange", {})
                            .get("timezone"),
                            "displayImgId": feature.get("properties", {})
                            .get("displayImage", {})
                            .get("id"),
                            "displayThumbUrl": feature.get("properties", {})
                            .get("displayImage", {})
                            .get("thumbUrl"),
                            "displayImgType": feature.get("properties", {})
                            .get("displayImage", {})
                            .get("type"),
                            "displayImgUrl": feature.get("properties", {})
                            .get("displayImage", {})
                            .get("url"),
                            "id": feature.get("properties", {}).get("id"),
                            "individual": feature.get("properties", {}).get(
                                "individual"
                            ),
                            "maxCount": feature.get("properties", {}).get("maxCount"),
                            "minCount": feature.get("properties", {}).get("minCount"),
                            "orgIds": feature.get("properties", {}).get("orgIds"),
                            "public": feature.get("properties", {}).get("public"),
                            "region": feature.get("properties", {}).get("region"),
                            "species": feature.get("properties", {}).get("species"),
                            "system:time_start": feature.get("properties", {}).get(
                                "system:time_start"
                            ),
                        }

                        flattened_data.append(flattened_feature)
                    except Exception as e:
                        logging.error(f"Subscription error for feature {i}: {e}")
                        continue
                flat_df = pd.DataFrame(flattened_data)
                flat_df.to_csv(export, index=False)
                logging.info(f"Search results exported to {export}")
            else:
                sys.exit(
                    "Could not export results choose from selected formats geojson/csv"
                )
        except Exception as error:
            logging.error(error)
    else:
        print(
            f"Search failed with status code {response.status_code} & message {response.json()['message']}"
        )


# geometry_search(geometry_file=r'C:\Users\samapriya\Downloads\aus.geojson',start='2023-09-01',end='2023-09-05',export='csv')


def search_from_parser(args):
    geometry_search(
        geometry_file=args.geom,
        start=args.start,
        end=args.end,
        export=args.export,
        species=args.species,
    )


def main(args=None):
    parser = argparse.ArgumentParser(description="Simple CLI for HappyWhale API")
    subparsers = parser.add_subparsers()

    parser_species = subparsers.add_parser(
        "species", help="Go to the web based pyaqua readme page"
    )
    parser_species.set_defaults(func=species_from_parser)

    parser_stats = subparsers.add_parser(
        "stats", help="Go to the web based pyaqua readme page"
    )
    optional_named = parser_stats.add_argument_group("Optional named arguments")
    optional_named.add_argument(
        "--st", help="Stats type encounters|users|individuals", default=None
    )
    parser_stats.set_defaults(func=stats_from_parser)

    parser_search = subparsers.add_parser(
        "search", help="Search and export results (Default: Global 1 month)"
    )
    required_named = parser_search.add_argument_group("Required named arguments.")
    required_named.add_argument(
        "--export",
        help="Full path to export file ending in .geojson or .csv",
        required=True,
    )
    required_named.add_argument(
        "--species",
        help="Species name or keyword for example Humpback Whale or humpback_whale",
        required=True,
        default=None,
    )
    optional_named = parser_search.add_argument_group("Optional named arguments")
    optional_named.add_argument(
        "--geom",
        help="Input geometry file in geojson format defaults to Global",
        default=None,
    )
    optional_named.add_argument(
        "--start", help="Start date in format YYYY-MM-DD", default=None
    )
    optional_named.add_argument(
        "--end", help="End date in format YYYY-MM-DD", default=None
    )
    parser_search.set_defaults(func=search_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
