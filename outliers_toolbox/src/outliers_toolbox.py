import pandas as pd


class Outliers:
    """
    Contains the information about the different outliers 
    for a certain column or list of columns
    :param dataframe: The dataframe used
    :param column: The name of the column that the person wants to test.
    There is lot of possibilities to enter columns:
    * Stri
    """
    def __init__ (
            self, 
            dataframe: pd.DataFrame, 
            column: str|list|int|pd.Series, 
        ) -> None:
        
        self.dataframe = dataframe
        self.column = column
        self.check_data_type()
        self.select_columns()
        
    def check_data_type(self):
        """
        This method is used to check the type of the differents arguments pass in the 
        constructor.
        """

        # Dataframe
        if not isinstance(self.dataframe, pd.DataFrame):
            raise TypeError(f"You have to enter a pandas dataframe, you enter {type(self.dataframe)}")

        # Column
        if not isinstance(self.column, (str, pd.Series, list, int)):
            raise TypeError(f"You have to specify. You enter {type(self.column)}")
    
    def select_columns(self):
        """
        This method is used to select the column that the participant wants to test. 
        This information is stored in the attribute self.columns_to_test. We want
        to obtain the name of each column.
        """
        # to select all columns
        if self.column == 'all':
            self.columns_to_test = list(df.columns)
        
        # if the participant enter the name of one column
        elif isinstance(self.column, str) and self.column != "all":

    
            if self.column not in df.columns:
                raise NameError("The column you enter is not in the dataframe")
            self.columns_to_test = self.column

        


if __name__=="__main__":
    df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep = ";")
    outliers = Outliers(df, column = True)    
    