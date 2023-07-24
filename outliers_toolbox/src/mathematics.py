import pandas as pd
import numpy as np

def compute_mad(df, column, median, b) -> float:
    distance_to_median = abs(df[column]-median)
    mad = np.median(distance_to_median)
    return mad*b