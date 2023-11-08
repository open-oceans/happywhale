import argparse
import concurrent.futures
import datetime
import getpass
import json
import logging
import os
import platform
import re
import subprocess
import sys
from os.path import expanduser

import geojson
import pandas as pd
import pkg_resources
import requests
from dateutil.relativedelta import *

# Set a custom log formatter
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

lpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(lpath)

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


class Solution:
    def compareVersion(self, version1, version2):
        versions1 = [int(v) for v in version1.split(".")]
        versions2 = [int(v) for v in version2.split(".")]
        for i in range(max(len(versions1), len(versions2))):
            v1 = versions1[i] if i < len(versions1) else 0
            v2 = versions2[i] if i < len(versions2) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0


ob1 = Solution()

if str(platform.system().lower()) == "windows":
    version = sys.version_info[0]
    try:
        import pipgeo

        response = requests.get("https://pypi.org/pypi/pipgeo/json")
        latest_version = response.json()["info"]["version"]
        vcheck = ob1.compareVersion(
            latest_version,
            pkg_resources.get_distribution("pipgeo").version,
        )
        if vcheck == 1:
            subprocess.call(
                f"{sys.executable}" + " -m pip install pipgeo --upgrade", shell=True
            )
    except ImportError:
        subprocess.call(f"{sys.executable}" + " -m pip install pipgeo", shell=True)
    except Exception as e:
        logging.exception(e)
    try:
        import gdal
    except ImportError:
        try:
            from osgeo import gdal
        except ModuleNotFoundError:
            subprocess.call("pipgeo sys", shell=True)
    except ModuleNotFoundError or ImportError:
        subprocess.call("pipgeo sys", shell=True)
    except Exception as e:
        logging.exception(e)
    try:
        import geopandas as gpd
    except ImportError:
        subprocess.call(f"{sys.executable}" + " -m pip install geopandas", shell=True)
        import geopandas as gpd
    except Exception as e:
        logging.exception(e)
else:
    try:
        import geopandas as gpd
    except ImportError:
        subprocess.call(f"{sys.executable}" + " -m pip install geopandas", shell=True)
        import geopandas as gpd
    except Exception as e:
        logging.exception(e)


# Get package version
def version_latest(package):
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    latest_version = response.json()["info"]["version"]
    return latest_version


def happywhale_version():
    vcheck = ob1.compareVersion(
        version_latest("happywhale"),
        pkg_resources.get_distribution("happywhale").version,
    )
    if vcheck == 1:
        print(
            "\n"
            + "========================================================================="
        )
        print(
            "Current version of happywhale is {} upgrade to lastest version: {}".format(
                pkg_resources.get_distribution("happywhale").version,
                version_latest("happywhale"),
            )
        )
        print(
            "========================================================================="
        )
    elif vcheck == -1:
        print(
            "\n"
            + "========================================================================="
        )
        print(
            "Possibly running staging code {} compared to pypi release {}".format(
                pkg_resources.get_distribution("happywhale").version,
                version_latest("happywhale"),
            )
        )
        print(
            "========================================================================="
        )


happywhale_version()

# Go to the readMe
def readme():
    try:
        a = webbrowser.open("https://happywhale.openoceans.xyz", new=2)
        if a == False:
            print("Your setup does not have a monitor to display the webpage")
            print(" Go to {}".format("https://happywhale.openoceans.xyz"))
    except Exception as error:
        print(error)


def read_from_parser(args):
    readme()

# set credentials
def auth():
    home = expanduser("~/hwhale.json")
    usr = input("Enter email: ")
    pwd = getpass.getpass("Enter password: ")
    while len(pwd) == 0:
        logging.error("Password cannot be empty")
        pwd = getpass.getpass("Enter password: ")
    data = {"email": usr, "password": pwd}
    with open(home, "w") as outfile:
        json.dump(data, outfile)
    json_data = {
        "username": usr,
        "password": pwd,
        "rememberMe": True,
    }
    response = requests.post(
        "https://critterspot.happywhale.com/v1/core/user/login",
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        logging.info("Logged in successfully")
    else:
        logging.error(f"Failed to login try again")

def auth_from_parser(args):
    auth()


def fetch_cookies():
    try:
        home = expanduser("~/hwhale.json")
        with open(home) as json_file:
            data = json.load(json_file)
            if not data.get("email"):
                email = input("Enter username: ")
            else:
                email = data.get("email")
            if not data.get("password"):
                password = getpass.getpass("Enter password: ")
            else:
                password = data.get("password")
    except Exception as e:
        print(e)

    json_data = {
        "username": email,
        "password": password,
        "rememberMe": True,
    }

    response = requests.post(
        "https://critterspot.happywhale.com/v1/core/user/login",
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        cookies = response.cookies.get_dict()
        return cookies
    else:
        print(f"Fetching cookies with response code {response.status_code}")


def species_config():
    response = requests.get(
        "https://critterspot.happywhale.com/v1/cs/encounter/config",
        headers=headers,
        cookies=fetch_cookies(),
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
        "https://critterspot.happywhale.com/v1/cs/main/sitestats",
        headers=headers,
        cookies=fetch_cookies(),
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
        f"https://critterspot.happywhale.com/v1/cs/encounter/full/{id}",
        headers=headers,
        cookies=fetch_cookies(),
    )
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(
            f"Request failed with {response.status_code} and error message {response.text}"
        )


def fetch_from_parser(args):
    id_fetch(id=args.id)


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


def encounter_full(id):
    response = requests.get(
        f"https://critterspot.happywhale.com/v1/cs/encounter/full/{id}", headers=headers
    )
    if response.status_code == 200:
        final_response = response.json()
        return final_response
    else:
        print(
            f"Request failed with {response.status_code} and error message {response.text}"
        )


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
    logging.info(
        f"Searching between Start date {str(start).split(' ')[0]} and End date {str(end).split(' ')[0]}"
    )
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
                    properties.pop("individual")
                    # properties["displayImg"] = properties.pop("displayImage")
                    properties["system:time_start"] = epoch_start(
                        properties["dateRange"]["startDate"]
                    )
                    object_id = properties.get("id")
                    object_detail = encounter_full(object_id)
                    accuracy = object_detail["encounter"]["location"].get("accuracy")
                    precision = object_detail["encounter"]["location"].get(
                        "precisionSource"
                    )
                    license = object_detail["encounter"]["displayImage"]["licenseLevel"]
                    if accuracy is not None:
                        properties["accuracy"] = accuracy
                    if precision is not None:
                        properties["precision"] = precision
                    if license is not None:
                        properties["license"] = license
                    # Create a Feature
                    feature = geojson.Feature(
                        geometry=geojson.Point((location["lng"], location["lat"])),
                        properties=properties,
                    )
                    features.append(feature)
                    print(
                        f"Processed {i+1} of {len(response.json())} encounters",
                        end="\r",
                    )
                except Exception as e:
                    logging.error(f"Subscription error for feature {i}: {e}")
                    continue
            feature_collection = geojson.FeatureCollection(features)
            geojson_data = geojson.dumps(feature_collection, sort_keys=True, indent=2)
            # print(geojson_data)
            if export.endswith("geojson"):
                with open(export, "w", encoding="utf-8") as geojson_file:
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
                            "accuracy": feature.get("properties", {}).get("accuracy"),
                            "precision": feature.get("properties", {}).get("precision"),
                            "displayImgLicense": feature.get("properties", {}).get(
                                "license"
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


def shorten_symbols(input_string):
    # Define a mapping of characters to symbols
    char_to_symbol = {
        "0": "A",
        "1": "B",
        "2": "C",
        "3": "D",
        "4": "E",
        "5": "F",
        "6": "G",
        "7": "H",
        "8": "I",
        "9": "J",
        "a": "K",
        "b": "L",
        "c": "M",
        "d": "N",
        "e": "O",
        "f": "P",
        "-": "Q",
    }

    shortened_string = "".join(char_to_symbol.get(c, c) for c in input_string)
    return shortened_string


def download_file_with_progress(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        if not os.path.exists(filename):
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            logging.info(f"Downloaded: {filename}")
        else:
            logging.info(f"Skipped existing file: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")


def downloader(download_list, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for entry in download_list:
            for filename, url in entry.items():
                full_path = os.path.join(output_folder, filename)
                future = executor.submit(download_file_with_progress, url, full_path)
                futures.append(future)
        concurrent.futures.wait(futures)


def photos_download(geometry_file, start, end, species, export):
    photo_dict = []
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
    logging.info(
        f"Searching between Start date {str(start).split(' ')[0]} and End date {str(end).split(' ')[0]}"
    )
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
                    properties = {k: v for k, v in json_obj.items() if k != "location"}
                    object_id = properties.get("id")
                    object_detail = encounter_full(object_id)
                    for photo in object_detail["photos"]:
                        uuid = shorten_symbols(
                            photo["url"].split("/")[-1].split(".")[0].replace("-", "")
                        )
                        img_name = f"IMG_{object_id}_{uuid}_{species.upper()}_{photo.get('licenseLevel')}.{photo['url'].split('/')[-1].split('.')[-1]}"
                        photo_dict.append({img_name: photo["url"]})
                    print(
                        f"Processed {i+1} of {len(response.json())} encounters",
                        end="\r",
                    )
                except Exception as e:
                    logging.error(f"Subscription error for feature {i}: {e}")
                    continue
        except Exception as error:
            logging.error(f"Encountered error {error}")
    print("\n" + f"Total image urls {len(photo_dict)}")
    downloader(photo_dict, export)


def download_from_parser(args):
    photos_download(
        geometry_file=args.geom,
        start=args.start,
        end=args.end,
        export=args.export,
        species=args.species,
    )


def main(args=None):
    parser = argparse.ArgumentParser(description="Simple CLI for HappyWhale.com")
    subparsers = parser.add_subparsers()
    parser_read = subparsers.add_parser(
        "readme", help="Go to the web based happywhale cli readme page"
    )
    parser_read.set_defaults(func=read_from_parser)

    parser_auth = subparsers.add_parser("auth", help="Saves your username and password")
    parser_auth.set_defaults(func=auth_from_parser)

    parser_species = subparsers.add_parser("species", help="Get species list")
    parser_species.set_defaults(func=species_from_parser)

    parser_stats = subparsers.add_parser("stats", help="Go site stats for happywhale")
    optional_named = parser_stats.add_argument_group("Optional named arguments")
    optional_named.add_argument(
        "--st", help="Stats type encounters|users|individuals", default=None
    )
    parser_stats.set_defaults(func=stats_from_parser)

    parser_fetch = subparsers.add_parser(
        "fetch", help="Fetch details on an encounter based on encounter id"
    )
    required_named = parser_fetch.add_argument_group("Required named arguments.")
    required_named.add_argument(
        "--id",
        help="Encounter id to fetch",
        required=True,
    )
    parser_fetch.set_defaults(func=fetch_from_parser)

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

    parser_download = subparsers.add_parser(
        "download", help="Download images from search results (Default: Global 1 month)"
    )
    required_named = parser_download.add_argument_group("Required named arguments.")
    required_named.add_argument(
        "--export",
        help="Full path to export folder to download images",
        required=True,
    )
    required_named.add_argument(
        "--species",
        help="Species name or keyword for example Humpback Whale or humpback_whale",
        required=True,
        default=None,
    )
    optional_named = parser_download.add_argument_group("Optional named arguments")
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
    parser_download.set_defaults(func=download_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
