from threshold import *
from mathematics import *

DICT_FUNCTION = {
    "iqr": threshold_iqr,
    "sd": threshold_sd,
    "mad": threshold_mad,
    "tukey": threshold_tukey,
    "sn": threshold_sn,
    "rsd": threshold_sd,
}