import sys
from main import app
from main import site_data, by_uid
from miniconf.load_site_data import load_site_data
load_site_data("/home/aaai2021_virtual/AAAI21-Virtual-Conference/sitedata", site_data, by_uid)