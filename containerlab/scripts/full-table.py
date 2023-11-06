import mrtparse
import gzip
import requests
import json
data = requests.get("https://data.ris.ripe.net/rrc00/2023.10/updates.20231031.1630.gz", stream=True)

if data.status_code == 200:
    for entry in mrtparse.Reader(gzip.GzipFile(fileobj=data.raw)):
        print(json.dumps(entry.data, indent=2))
        break
else:
    print("Sadly no full-table here.")
