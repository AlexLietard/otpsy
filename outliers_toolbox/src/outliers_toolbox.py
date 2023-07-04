import pandas as pd
pd.DataFrame
class Outliers:
    """
    Contains the information about the different outliers 
    for a certain column or list of columns
    """
    def __init__(self, dataframe: pd.DataFrame, column:list|str) -> None:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"You have to enter a pandas dataframe, you enter {type(dataframe)}")
        else:
            self.dataframe = dataframe
        self.column = column

      
    