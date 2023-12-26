import otpsy.src.threshold as th

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

HEXA_FOR_PLOTLY = {
    "iqr": "#D1F5BE",
    "sd": "#9DB17C",
    "rsd" : "#4B3B40"
}