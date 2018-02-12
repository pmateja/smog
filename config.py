import os
import yaml


#  If conf in ~/.smog/config.yaml exist, override classes above
home_conf = os.path.join(
        os.path.expanduser("~"),
        ".config/smog", "config.yaml")
local_conf = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "config.yaml")
if os.path.isfile(home_conf):
    conf = yaml.load(open(home_conf))
else:
    conf = yaml.load(open(local_conf))