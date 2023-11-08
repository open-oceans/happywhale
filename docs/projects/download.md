# Download images

The download tool is designed to fetch captures images/photos from encounter search. It renames the filenames to reduce the UUID length. The downloader is a multi-threaded download processer that fetches the images from the search list and downloads them to the export folder.

The filename structure is

```
IMG_**ENCOUNTER-ID**_**ENCODED-FILENAME**_**SPECIES**_**LICENSE**.**format**
```

for example:

**IMG_324585_MHNNPJCAHCLEEGKFLLAFMPJFNAOJGIMC_HUMPBACK_WHALE_PUBLIC_DOMAIN.jpg**

![happy_download](https://github.com/open-oceans/happywhale/assets/6677629/50009bca-6029-4f8d-86d7-2809cf1770d7)

```
happywhale download -h
usage: happywhale download [-h] --export EXPORT --species SPECIES [--geom GEOM] [--start START] [--end END]

options:
  -h, --help         show this help message and exit

Required named arguments.:
  --export EXPORT    Full path to export folder to download images
  --species SPECIES  Species name or keyword for example Humpback Whale or humpback_whale

Optional named arguments:
  --geom GEOM        Input geometry file in geojson format defaults to Global
  --start START      Start date in format YYYY-MM-DD
  --end END          End date in format YYYY-MM-DD
```
