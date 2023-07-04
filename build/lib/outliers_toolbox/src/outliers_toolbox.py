import pandas as pd
pd.read_csv
class Outliers:
    """
    Contains the information about the different outliers 
    for a certain column or list of columns
    """
    def __init__(self, dataframe: pd.DataFrame, column:list|str) -> None:
        self.dataframe = dataframe
        self.column = column
      
    