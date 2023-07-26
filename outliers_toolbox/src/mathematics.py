import pandas as pd
import numpy as np

def compute_mad(df, column, median, b) -> float:
    distance_to_median = abs(df[column]-median)
    mad = np.nanmedian(distance_to_median)
    return mad*b

def S_n(self, column):
    n = len(self.df[column])
    all_median = {}
    
    if n < 10:
        c_depending_n = [0, 0.743, 1.851, 0.954, 1.351, 0.993, 1.198, 1.005, 1.131]
        c = c_depending_n[n-1]
    elif n%2 == 1:
        c = n/(n-0.9)
    else:
        c = 1
    
    for i, i_value in enumerate(self.df[column]):
        distance_to_i = []
        for j, j_value in enumerate(self.df[column]):
            if i != j:
                distance = abs(float(i_value)-float(j_value))
                distance_to_i.append(distance)
        all_median[i] = np.median(distance_to_i)
    
    Sn = np.median(list(all_median.values())) * c
    return Sn, all_median