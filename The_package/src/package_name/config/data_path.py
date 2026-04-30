import os

DATA_PATH = os.getenv("DATA_PATH", "/Users/arjan/datasets/osm/")
PBF_FILE = os.path.join(DATA_PATH, "amsterdam.osm.pbf")

GTFS_FILE = os.path.join(DATA_PATH, "test_gtfs.zip")