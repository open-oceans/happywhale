import argparse
import getpass
import json
import logging
import re
import sys

import requests
from tabulate import tabulate

# Set a custom log formatter
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://happywhale.com',
    'Referer': 'https://happywhale.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def auth():
    json_data = {
        'username': 'roysam@hawaii.edu',
        'password': 'ydg9bpd3AGD9zmy.fdq',
        'rememberMe': True,
    }

    response = requests.post('https://critterspot.happywhale.com/v1/core/user/login', headers=headers, json=json_data)
    print(json.dumos(response.json()))
#auth()

def species_config():
    response = requests.get('https://critterspot.happywhale.com/v1/cs/encounter/config', headers=headers)
    if response.status_code == 200:
        species_code = [[item.get('name'),item.get('code')] for item in response.json()['species']]
        if len(species_code)>0:
            print("\n" + "================Species Name: Species Code================")
            print(
                "\n".join([" : ".join([str(cell) for cell in row]) for row in species_code])
            )
    else:
        logging.error(f'Failed to get species config with error code: {response.status_code}')
def species_from_parser(args):
    species_config()

def stats(stat_type):
    response = requests.get('https://critterspot.happywhale.com/v1/cs/main/sitestats', headers=headers)
    if response.status_code == 200:
        # total photos
        total_photos = response.json()['site']['numPhotos']
        # user stats
        total_users = response.json()['site']['users']['num']
        top_contributors = response.json()['site']['users']['topContribs']
        top_contributors_year = response.json()['site']['users']['topContribsLastYear']

        # encounter stats
        encounters_total = response.json()['site']['encounters']['num']
        encounters_total_ided = response.json()['site']['encounters']['numIded']
        encounters_recent = response.json()['site']['encounters']['mostRecent']
        encounters_recent_ided = response.json()['site']['encounters']['mostRecentIded']
        encounters_species = response.json()['site']['encounters']['bySpecies']

        # individuals stats
        individuals_total = response.json()['site']['individuals']['num']
        furthest_sighted = response.json()['site']['individuals']['furthestSighted']
        longest_time_between = response.json()['site']['individuals']['longestTimeBetween']
        longest_first_last = response.json()['site']['individuals']['longestFirstLast']
        most_sighted = response.json()['site']['individuals']['mostSighted']

        ############### Print stats ###############
        logging.info(f'Total photos: {total_photos:,}')
        logging.info(f'Total users: {total_users:,}')
        logging.info(f'Total encounters {encounters_total:,}')
        logging.info(f'Total encounters ided: {encounters_total_ided:,}')
        logging.info(f'Encountered species: {len(encounters_species):,}')
        logging.info(f'Individuals total: {individuals_total}')
        #logging.info(f'Encounters recent ided: {len(encounters_recent_ided):,}')
        #logging.info(f'Furthest sighted: {len(furthest_sighted)}')
        #logging.info(f'most sighted: {len(most_sighted)}')
        if stat_type == 'user' or stat_type == 'users':
            print("\n" + f'Now fetching total of {len(top_contributors):,} top contributors')
            #top_contributors['user'])
            user_code = [[item['user'].get('displayName'),item.get('numEncs'),item.get('numPhotos'),item.get('rank')] for item in top_contributors]
            if len(user_code)>0:
                print("\n" + "================Top 10 Current Users================")
                for user in user_code:
                    display_name = re.sub(r'\b\w', lambda x: x.group(0).upper(),user[0].lower())
                    print(f"User/Org {display_name} with rank {user[3]}: Total enncounters {user[1]:,} and {user[2]:,} photos")
        if stat_type == 'individuals' or stat_type == 'individual':
            print("\n" + f'Now fetching total of {len(most_sighted):,} most sighted individuals')
            user_code = [[item['individual'].get('nickname'),item['individual'].get('species'),item['individual'].get('sex'),item.get('stat')] for item in most_sighted]
            if len(user_code)>0:
                print("\n" + "================Most Sighted Individuals Stats================")
                for user in user_code:
                    display_name = re.sub(r'\b\w', lambda x: x.group(0).upper(),user[0].lower())
                    print(f"{user[1]} with nickname {display_name} with {user[3]}: Total enncounters")
        if stat_type == 'encounters' or stat_type == 'encounter':
            print("\n" + f'Now fetching total of {len(encounters_recent_ided)} encounters')
            user_code = [[item['encounter']['species'],item['encounter']['region'],item['encounter']['dateRange']['startDate'],item['encounter']['id']] for item in encounters_recent_ided]
            if len(user_code)>0:
                print("\n" + "================Most Recent Encounters================")
                for user in user_code:
                    print(f"Encountered {user[0]} with encounter id {user[3]} in the {user[1]} region, on {user[2]}")
def stats_from_parser(args):
    stats(stat_type=args.st)

response = requests.get('https://critterspot.happywhale.com/v1/cs/encounter/full/362688', headers=headers)
print(json.dumps(response.json(),indent=2))
# print(species_code)
# response = requests.get('https://critterspot.happywhale.com/v1/core/media/config', headers=headers)


#print(json.dumps(response.json(),indent=2))
# for obs in response.json()['encounter']:
#     print(obs)
#     print('')

def search():
    json_data = {
    'encounter': {
        'datesearch': {
            # 'preset':2,
            # 'type': 4,
            'startdate': '2010-10-01',
            'enddate': '2023-11-01',
        },
        'species': 'humpback_whale',
    },
    'showConnections': False,
    }

    response = requests.post(
        'https://critterspot.happywhale.com/v1/cs/admin/encounter/search',
        headers=headers,
        json=json_data,
    )
    print(response.text)
    print(response.status_code)
    for item in response.json():
        print(item)
#search()



def geometry_search():
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://happywhale.com',
        'Referer': 'https://happywhale.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'showConnections': False,
        'encounter': {
            'species': 'humpback_whale',
            'datesearch': {
                # 'preset':2,
                # 'type': 4,
                'startdate': '2010-12-01',
                'enddate': '2023-11-01',
            },
            # 'locsearch': {
            #     'type': 'mapbounds',
            #     'watergeo': None,
            #     'mapBounds': {
            #         'southWest': {
            #             'lat': -40.02340800226772,
            #             'lng': -74.16892858197295,
            #         },
            #         'northEast': {
            #             'lat': -37.4530574713902,
            #             'lng': -71.86729283978545,
            #         },
            #     },
            # },
        },
    }

    response = requests.post('https://critterspot.happywhale.com/v1/cs/admin/encounter/search', headers=headers, json=json_data)
    #print(response.text)
    print(len(response.json()))
    # for i,item in enumerate(response.json()):
    #     if i<=1:
    #         print(item)

#geometry_search()

import requests

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://happywhale.com',
    'Referer': 'https://happywhale.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

json_data = {
    'showConnections': False,
    'encounter': {
        'species': 'humpback_whale',
        'locsearch': {
            'type': 'mapbounds',
            'watergeo': None,
            'mapBounds': {
                'southWest': {
                    'lat': 7.798078531355303,
                    'lng': -159.47753906250003,
                },
                'northEast': {
                    'lat': 32.32427558887655,
                    'lng': -152.27050781250003,
                },
            },
        },
        'datesearch': {
            'startdate': '2022-01-01',
            'type': 3,
            'enddate': '2023-11-30',
        },
    },
}

response = requests.post('https://critterspot.happywhale.com/v1/cs/admin/encounter/search', headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"showConnections":false,"encounter":{"species":"humpback_whale","locsearch":{"type":"mapbounds","watergeo":null,"mapBounds":{"southWest":{"lat":7.798078531355303,"lng":-159.47753906250003},"northEast":{"lat":32.32427558887655,"lng":-152.27050781250003}}},"datesearch":{"startdate":"2022-01-01","type":3,"enddate":"2023-11-30"}}}'
#response = requests.post('https://critterspot.happywhale.com/v1/cs/admin/encounter/search', headers=headers, data=data)
print(len(response.json()))
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
    optional_named.add_argument("--st", help="Stats type encounters|users|individuals", default=None)
    parser_stats.set_defaults(func=stats_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
