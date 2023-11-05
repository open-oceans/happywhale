import argparse
import getpass
import json
import logging
import sys

import requests

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

def stats():
    response = requests.get('https://critterspot.happywhale.com/v1/cs/main/sitestats', headers=headers)
    for subsets in response.json()['site']:
        print(subsets)
    total_users = response.json()['site']['users']['num']
    top_contributors = response.json()['site']['users']['topContribs']
    print(json.dumps(response.json()['site']['encounters']))
    #print(json.dumps(response.json(),indent=2))

def stats_from_parser(args):
    stats()

# response = requests.get('https://critterspot.happywhale.com/v1/cs/encounter/full/395867', headers=headers)

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



def quick_look(look_type):
    look_type_list = {
        'recent':'mostRecent',
        'recent_id':'mostRecentIded',
        'species':'bySpecies',
    }
    response = requests.get('https://critterspot.happywhale.com/v1/cs/main/sitestats', headers=headers)
    # for subsets in response.json()['site']:
    #     print(subsets)
    if look_type in look_type_list.keys():
        print(look_type_list.get(look_type))
    encounters = response.json()['site']['encounters'][look_type_list.get(look_type)]
    print(json.dumps(encounters,indent=2))
    total_num = response.json()['site']['encounters']['num']
    total_num_ided = response.json()['site']['encounters']['numIded']
    print(f'Total encounters were {total_num} with {total_num_ided} ided encounters')
    # for things in encounters:
    #     print(things)
    # # total_users = response.json()['site']['users']['num']
    # # top_contributors = response.json()['site']['users']['topContribs']
    # print(json.dumps(encounters,indent=2))
#quick_look(look_type='recent_id')

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
            'species': 'fur_seal_antarctic',
            'locsearch': {
                'type': 'mapbounds',
                'watergeo': None,
                'mapBounds': {
                    'southWest': {
                        'lat': -40.02340800226772,
                        'lng': -74.16892858197295,
                    },
                    'northEast': {
                        'lat': -37.4530574713902,
                        'lng': -71.86729283978545,
                    },
                },
            },
        },
    }

    response = requests.post('https://critterspot.happywhale.com/v1/cs/admin/encounter/search', headers=headers, json=json_data)
#geometry_search()

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
    parser_stats.set_defaults(func=stats_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
