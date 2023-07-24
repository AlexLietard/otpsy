import pandas as pd
import numpy as np
from utils import check
import mathematics


@check
def threshold_iqr(
    df: pd.DataFrame,
    column_to_test: str,
    distance: float | int
) -> float:
    """ IQR outlier method

    This function allow the user to have the low threshold
    and the high threshold with the "IQR" outliers method
    with a specific distance.

    Parameters
    ------------
        df: pd.DataFrame
            The dataframe used
        column: str | list | int | pd.Series
            The name of the colum of interest
        distance: float | int
            The distance used to calculate threshold
    """
    # calculate the interquartile range and the median
    ret = {}
    for column in column_to_test:
        q1, q3 = df[column].quantile([0.25, 0.75])
        iqr = q3-q1

        med = np.nanmedian(df[column])
        print(med)

        # threshold
        low_threshold = med - (distance * iqr)
        high_threshold = med + (distance * iqr)

        ret[column] = (low_threshold, high_threshold)

    # avoid having a dictionnary for one column
    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret


@check
def threshold_sd(
    df: pd.DataFrame,
    column_to_test: str,
    distance: float | int
) -> float:
    """ SD outlier method

    This function allow the user to have the low threshold
    and the high threshold with the "SD" outliers method
    with a specific distance.

    Parameters
    ------------
        df: pd.DataFrame
            The dataframe used
        column: str | list | int | pd.Series
            The name of the colum of interest
        distance: float | int
            The distance used to calculate threshold
    """
    # calculate the interquartile range and the median
    ret = {}
    for column in column_to_test:
        sd = np.nanstd(df[column])

        # Pareil que IQR
        moy = np.nanmean(df[column])

        # définition des bornes
        low_threshold = moy - distance * sd
        high_threshold = moy + distance * sd

        ret[column] = (low_threshold, high_threshold)

    # avoid having a dictionnary for one column
    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret


@check
def threshold_mad(
    df: pd.DataFrame,
    column_to_test: str,
    distance: float | int
) -> float:
    """ MAD detection method

    This function allow the user to have the low threshold
    and the high threshold with the "MAD" outliers method
    with a specific distance.

    Parameters
    ------------
        df: pd.DataFrame
            The dataframe used
        column: str | list | int | pd.Series
            The name of the colum of interest
        distance: float | int
            The distance used to calculate threshold
    """
    ret = {}
    for column in column_to_test:
        med = np.nanmedian(df[column])
        b = 1.4826
        mad = mathematics.compute_mad(df, column, med, b)

        # threshold
        low_threshold = med - (distance * mad)
        high_threshold = med + (distance * mad)

        ret[column] = (low_threshold, high_threshold)
    print(ret)
    # avoid having a dictionnary for one column
    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret
