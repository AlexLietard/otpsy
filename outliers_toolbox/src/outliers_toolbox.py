import pandas as pd


class Outliers:
    """
    Contains the information about the different outliers 
    for a certain column or list of columns
    :param dataframe: The dataframe used
    :param column: The name of the column that the person wants to test
    :param columns: The names of the columns that the person wants to test.
    """
    def __init__ (
            self, 
            dataframe: pd.DataFrame = None, 
            column: str = "", 
            columns: list = []
        ) -> None:
        
        self.dataframe = dataframe
        self.column = column
        self.columns = columns
        self.check_data_type()
        
    def check_data_type(self):
        """
        This method is used to check the type of the differents arguments pass in the 
        constructor.
        """

        # Dataframe
        if not isinstance(self.dataframe, pd.DataFrame):
            raise TypeError(f"You have to enter a pandas dataframe, you enter {type(self.dataframe)}")

        # Column
        if not isinstance(self.column, str):
            # Special case if it is a list, to allow people to know that there exist column and columnS.
            if isinstance(self.column, list):
                raise TypeError(f"You have enter a list while we expected string. You have to enter only one name of column if you use 'column', instead use 'columns'.")
            elif isinstance(self.column, pd.Series):
                raise TypeError(f"You have to enter the name of the column and not the panda")
            else:
                raise TypeError(f"Expected string, you enter {type(self.column)}")
        
        # Columns
        if not isinstance(self.columns, list):
            raise TypeError(f"You have to enter multiple columns with a list of string, you enter {type(self.columns)}")


if __name__=="__main__":
    df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep = ";")

    outliers = Outliers("df", columns = ["bla", 'bla'])    
    