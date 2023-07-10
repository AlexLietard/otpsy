import pandas as pd
from pandas.api.types import is_numeric_dtype

class Outliers:
    """
    Contains the information about the different outliers 
    for a certain column or list of columns
    :param dataframe: The dataframe used
    :param column: The column that the user wants to test.
    """
    def __init__(
            self, 
            dataframe: pd.DataFrame, 
            column: str|list|int|pd.Series,
            participant_column : str|int|pd.Series
        ) -> None:
        
        self.df = dataframe
        self.column = column
        self.participant_column = participant_column
        self.__check_data_type()
        self.__select_columns_to_test()
        self.__define_participant_column()
        self.__check_if_numeric()
    
    def __check_data_type(self):
        """
        This method is used to check the type of the differents arguments pass in the 
        constructor.
        """

        # Dataframe
        if not isinstance(self.df, pd.DataFrame):
            raise TypeError(f"You have to enter a pandas dataframe, you enter {type(self.df)}")

        # Column
        if not isinstance(self.column, (str, pd.Series, list, int)):
            raise TypeError(f"You have to specify the column. You enter {type(self.column)}")
        
        # Participant column
        if not isinstance(self.participant_column, (str, pd.Series, int)):
            raise TypeError(f"You have to specify the participant column. You enter {type(self.participant_column)}")
     
    def __select_columns_to_test(self):
        """
        This method is not designed to be used by users.
        This method is used to select the column(s) that the user wants to test. 
        This information is stored in the attribute self.columns_to_test. We want
        to obtain the name of each column in a list of column name.
        """
        self.columns_to_test = []

        # if the user enters the Series
        if isinstance(self.column, pd.Series):
            self.columns_to_test.append(self.column.name)

        # to select all columns
        elif self.column == 'all':
            self.columns_to_test.extend(list(self.df.columns))
        
        # if the person enters the name of one column
        elif isinstance(self.column, str):
            if self.column not in self.df.columns:
                raise NameError("The column you enter is not in the dataframe")
            else:
                self.columns_to_test.append(self.column)
        
        # if the person enters the index of the column
        elif isinstance(self.column, int):
            self.columns_to_test.append(self.df.iloc[:, self.column].name)

        # if the person enters a list
        elif isinstance(self.column, list):

            # There is three possibilities : either it contains the name of the columns,
            # either it contains the pd.Series, either it contains a list of index

            for column in self.column:
                # If it's column
                if isinstance(column, pd.Series):
                    self.columns_to_test.append(column.name)

                # If it's name, check its presence in the dataframe
                elif isinstance(column, str):
                    if column not in self.df.columns:
                        raise NameError(f"The column \"{column}\" you enter is not in the dataframe")
                    else:
                        self.columns_to_test.append(column)
                
                # it is the index of column
                elif isinstance(column, int):
                    self.columns_to_test.append(self.df.iloc[:, column].name)
        
        # Avoid potential duplicates
        self.columns_to_test = list(set(self.columns_to_test))

    def __define_participant_column(self):
        if isinstance(self.participant_column, pd.Series):
            self.participant_column = self.participant_column.name
        elif isinstance(self.participant_column, int):
            self.participant_column = self.df.iloc[:, self.participant_column].name
        elif isinstance(self.participant_column, str):
            if self.participant_column not in self.df.columns:
                raise NameError("The column you enter is not in the dataframe")
            else:
                self.participant_column = self.participant_column
        
        # avoid potential overlap between column to test and participant column
        if self.participant_column in self.columns_to_test:
            raise ValueError("The participant column can't be in the columns you want to test")
                
    def __check_if_numeric(self):
        not_numeric = []
        for column in self.columns_to_test:
            if not is_numeric_dtype(column):
                not_numeric.append(column)

        if len(not_numeric) > 0:
            raise TypeError(f"{not_numeric} is not numeric. Thus, the outlier detection wont be possible.")
        
        self.columns_to_test = list(set(self.columns_to_test) - set(not_numeric))

    def calculate_iqr(self):
        pass


            
        


if __name__ == "__main__":
    df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep = ";")
    outliers = Outliers(df, ["premiere_lettre", df["CLI1"]], "DIF1")
    print(outliers.columns_to_test)
    