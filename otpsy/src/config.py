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
    "mad" : "#4B3B40",
    "sd": "#9DB17C",
    "rsd" : "#4B3B40",
    "tukey" : "#4B3B40",
    "prctile" : "#4B3B40",
    "cut-off" : "#4B3B40",
}