# Search and export

The search and export tool is designed to search the database based on species information. Some defaults are maintained such as if no geometry is provided a global geometry is assumed and if no date ranges are provided a month is chosen from currrent date. If only start or end dates are provided a month is added to the start or deducted from the end date. The tool fetches additional information like geolocation accuracy and license information and adds it to the export. The export can be a GeoJSON file or a CSV.

![happy_search](https://github.com/open-oceans/happywhale/assets/6677629/495c1886-5594-41f9-a7c6-35b58e30404d)

The bare minima arguments required are an export file path and the species. The tool will automatically select one month from today and use a global geometry to run the search.

![happy_search_global](https://github.com/open-oceans/happywhale/assets/6677629/f62b531b-8bf9-4140-923d-be19764ff493)

```
happywhale search -h
usage: happywhale search [-h] --export EXPORT --species SPECIES [--geom GEOM] [--start START] [--end END]

options:
  -h, --help         show this help message and exit

Required named arguments.:
  --export EXPORT    Full path to export file ending in .geojson or .csv
  --species SPECIES  Species name or keyword for example Humpback Whale or humpback_whale

Optional named arguments:
  --geom GEOM        Input geometry file in geojson format defaults to Global
  --start START      Start date in format YYYY-MM-DD
  --end END          End date in format YYYY-MM-DD
```
