import os
import shutil
from pathlib import Path

import wget

ROOT = Path(__file__).parent.absolute()
PATH_DOWNLOADS = ROOT / "downloads"
PATH_YAMLS = ROOT / "yamls"

URL_SLIDESLIVE_OTHER = "https://docs.google.com/spreadsheets/d/1Cp04DGRiDj8oY00-xDjTpjzCd_fjq3YhqOclhvFRK94/export?format=csv&gid=1157572740"
PATH_SLIDESLIVE_OTHER = PATH_DOWNLOADS / "slideslive_other.csv"

URL_SLIDESLIVE_WORKSHOPS = "https://docs.google.com/spreadsheets/d/1Cp04DGRiDj8oY00-xDjTpjzCd_fjq3YhqOclhvFRK94/export?format=csv&gid=1798866366"
PATH_SLIDESLIVE_WORKSHOPS = PATH_DOWNLOADS / "slideslive_workshops.csv"

URL_TUTORIALS_SCHEDULE = "https://docs.google.com/spreadsheets/d/16kLECn6WZNXfbj_8CL1QJykHVndijMCcyWT3rl9jOhI/export?format=xlsx"
PATH_TUTORIALS_SCHEDULE = PATH_DOWNLOADS / "tutorials.xlsx"

URL_TUTORIALS_OVERVIEW = "https://raw.githubusercontent.com/emnlp2020/emnlp2020-website/master/src/data/tutorials.csv"
PATH_TUTORIALS_OVERVIEW = PATH_DOWNLOADS / "tutorials.csv"

URL_WORKSHOPS_OVERVIEW = "https://docs.google.com/spreadsheets/d/19LRnJpae5NQd0D1NEO40kTbwDvS9f125tpsjBdevrcs/export?format=xlsx"
PATH_WORKSHOPS_OVERVIEW = PATH_DOWNLOADS / "workshops.xlsx"

URL_WORKSHOPS_SCHEDULE = "https://docs.google.com/spreadsheets/d/1BgDuZLKm8rlX-o8l61jAcOrwoKXG6SKhbvjv5-ub2Iw/export?format=xlsx"
PATH_WORKSHOPS_SCHEDULE = PATH_DOWNLOADS / "workshops_schedule.xlsx"

URL_WORKSHOPS_CSV = "https://raw.githubusercontent.com/emnlp2020/emnlp2020-website/master/src/data/workshops.csv"
PATH_WORKSHOPS_CSV = PATH_DOWNLOADS / "workshops.csv"

URL_WORKSHOP_TALKS = "https://docs.google.com/spreadsheets/d/1xw-R1sMfLLX2gZ8CTGRn1Q1wiLR8y5O16To34m_H0oQ/export?format=xlsx"
PATH_WORKSHOP_TALKS = PATH_DOWNLOADS / "workshop_talks.csv"

URL_SOCIALS = "https://docs.google.com/spreadsheets/d/1IDk3K1JD1hvH_hvyMy6TeRuE2F6DQDfpgwNpTIP9KgI/export?format=xlsx"
PATH_SOCIALS = PATH_DOWNLOADS / "socials.xlsx"

URL_ZOOMS_ACCOUNTS_WITH_PASSWORDS = "https://docs.google.com/spreadsheets/d/1dg2By1lGyFuY_jBG9t1JDnYFx0UhdHl8jUuqqe0-5v8/export?format=xlsx"
PATH_ZOOM_ACCOUNTS_WITH_PASSWORDS = PATH_DOWNLOADS / "zoom_accounts_with_passwords.xlsx"

URL_ZOOMS_ACCOUNTS_SCHEDULED = "https://docs.google.com/spreadsheets/d/1LTVmbJ2XUnMKM_Tw6UqtuUSxW-roiz_ifJEtX2J7qtE/export?format=xlsx"
PATH_ZOOM_ACCOUNTS_SCHEDULED = PATH_DOWNLOADS / "zoom_accounts_scheduled.xlsx"

PATH_DOWNLOADS.mkdir(exist_ok=True, parents=True)
PATH_YAMLS.mkdir(exist_ok=True, parents=True)


def download_file(url: str, out: Path):
    out.unlink(missing_ok=True)
    wget.download(url, str(out))


def download_slideslive():
    download_file(URL_SLIDESLIVE_OTHER, PATH_SLIDESLIVE_OTHER)
    download_file(URL_SLIDESLIVE_WORKSHOPS, PATH_SLIDESLIVE_WORKSHOPS)


def download_tutorials():
    download_file(URL_TUTORIALS_SCHEDULE, PATH_TUTORIALS_SCHEDULE)
    download_file(URL_TUTORIALS_OVERVIEW, PATH_TUTORIALS_OVERVIEW)


def download_workshops():
    download_file(URL_WORKSHOPS_OVERVIEW, PATH_WORKSHOPS_OVERVIEW)
    download_file(URL_WORKSHOPS_SCHEDULE, PATH_WORKSHOPS_SCHEDULE)
    # download_file(URL_WORKSHOPS_CSV, PATH_WORKSHOPS_CSV)
    download_file(URL_WORKSHOP_TALKS, PATH_WORKSHOP_TALKS)


def download_socials():
    download_file(URL_SOCIALS, PATH_SOCIALS)


def download_zooms():
    # download_file(URL_ZOOMS_ACCOUNTS_WITH_PASSWORDS, PATH_ZOOM_ACCOUNTS_WITH_PASSWORDS)
    # download_file(URL_ZOOMS_ACCOUNTS_SCHEDULED, PATH_ZOOM_ACCOUNTS_SCHEDULED)
    pass
