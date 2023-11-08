# Fetch encounter info

This tool was designed to extract extra bits of information about encounters from the happywhale search results and a specific encounter. The returned result is a JSON object containing details of the encounter.

#### Fetch Encounter ID
Let's first fetch the ID for an encounter from the happywhale webpage.

![happy_whale_online](https://github.com/open-oceans/happywhale/assets/6677629/d6ac498d-c29b-4029-939e-8aa0bafe69d0)

#### Fetch Encounter Details
Now let's use the encounter ID to fetch the encounter details

![happy_whale_fetch](https://github.com/open-oceans/happywhale/assets/6677629/4ffac35e-57ff-4925-a079-d6ab6f01a474)

```
happywhale fetch -h
usage: happywhale fetch [-h] --id ID

options:
  -h, --help  show this help message and exit

Required named arguments.:
  --id ID     Encounter id to fetch
```
