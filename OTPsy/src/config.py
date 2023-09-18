from . import threshold as th

DICT_FUNCTION = {
    "iqr": th.threshold_iqr,
    "sd": th.threshold_sd,
    "mad": th.threshold_mad,
    "tukey": th.threshold_tukey,
    "sn": th.threshold_sn,
    "rsd": th.threshold_sd,
    "prctile": th.threshold_prctile,
    "identical": th.threshold_identical,
}