from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import pandas as pd
import dateutil.parser

from ruamel import yaml
import ruamel

from scripts.dataentry.paths import PATH_YAMLS, PATH_ZOOM_ACCOUNTS_WITH_PASSWORDS

root = Path(r"D:\Dropbox\emnlp2020\sponsors\clean\yamls")


def main():
    sponsors = []

    def timestamp_constructor(loader, node):
        return dateutil.parser.parse(node.value)

    yaml.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)

    zoom_df = pd.read_excel(
        PATH_ZOOM_ACCOUNTS_WITH_PASSWORDS, sheet_name="Sponsors"
    ).fillna("")

    zooms = []
    zoom_names = []
    for _, row in zoom_df.iterrows():
        zooms.append(row["Personal Meeting LINK"])
        zoom_names.append(row["uniqueid"])

    for sponsor_yaml in sorted(root.iterdir()):
        with sponsor_yaml.open() as f:
            raw_sponsor = yaml.load(f, Loader=ruamel.yaml.Loader)
            sponsor = raw_sponsor
        sponsors.append(sponsor)

    for i, sponsor in enumerate(sponsors):
        sponsor_name = sponsor["name"].lower().replace(" ", "-").replace(",", "")
        if "hitachi" in sponsor_name.lower():
            sponsor_name = "hitachi"
        sponsor["rocketchat_channel"] = f"sponsor-{sponsor_name}"
        if "zoom_link" not in sponsor:
            assert sponsor["name"] in zoom_names[i], (sponsor["name"], zoom_names[i])
            sponsor["zoom_link"] = zooms[i]
        else:
            # print(sponsor_name, sponsor["zoom_link"])
            pass

    yaml.scalarstring.walk_tree(sponsors)

    with open(PATH_YAMLS / "sponsors.yml", "w") as f:
        yaml.dump(sponsors, f, Dumper=ruamel.yaml.RoundTripDumper)


if __name__ == "__main__":
    main()
