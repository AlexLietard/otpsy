import pandas as pd
import numpy as np


# Median Absolute Distance
def compute_mad(df, column, median, b) -> float:
    distance_to_median = abs(df[column]-median)
    mad = np.nanmedian(distance_to_median)
    return mad*b

# Sn


def select_c(n):
    if n < 10:
        c_depending_n = [0, 0.743, 1.851, 0.954,
                         1.351, 0.993, 1.198, 1.005, 1.131]
        c = c_depending_n[n-1]
    elif n % 2 == 1:
        c = n/(n-0.9)
    else:
        c = 1
    return c


def S_n(df, column):
    n = len(df[column])
    c = select_c(n)

    # create a dataframe with index and median distance to other point
    all_median = df[[column]].apply(lambda x: np.nanmedian(
        abs(x[column] - df.loc[df.index != x.name, column])), axis=1)
    
    Sn = np.nanmedian(all_median) * c
    return Sn, all_median



