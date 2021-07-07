from typing import List

import pandas as pd
import yaml

WORKSHOPS_YAML = "../../sitedata/workshops.yml"
WORKSHOPS_PAPERS_CSV = "../../sitedata/workshop_papers.csv"


def get_workshop_channels() -> List[str]:
    with open(WORKSHOPS_YAML, "r") as f:
        workshops = yaml.safe_load(f)

    return [w["rocketchat_channel"] for w in workshops]


def get_workshop_paper_channels() -> List[str]:
    with open(WORKSHOPS_YAML, "r") as f:
        workshops = yaml.safe_load(f)

    ws_id_to_alias = {w["UID"]: w["alias"] for w in workshops}

    df = pd.read_csv(WORKSHOPS_PAPERS_CSV)

    channels = []
    for _, row in df.iterrows():
        paper_id = row["UID"]
        workshop_id = row["workshop"]
        alias = ws_id_to_alias[workshop_id]
        channel = f"paper-{alias}-{paper_id.split('.')[-1]}"
        channels.append(channel)

    return channels


if __name__ == "__main__":
    print(get_workshop_channels())
    print(get_workshop_paper_channels())
