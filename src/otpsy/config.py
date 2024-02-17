import src.otpsy.threshold as th

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
    "iqr": "#00b4d8",
    "mad" : "#F39237",
    "sd": "#9DB17C",
    "rsd" : "#643A71",
    "tukey" : "#FEC0CE",
    # "prctile" : "#4B3B40",
    # "cut-off" : "#4B3B40",
}