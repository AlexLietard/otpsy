import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
from inspect import getcallargs

def check(function):
    """ Decorator to transform argument in the good format

    For every parameters possible in the dataframe, there is
    a check of the arguments passed. 
    """
    def select_columns_to_test(*args, **kwargs):
        new_kwargs = {}
        kwargs = getcallargs(function, *args, **kwargs)
        
        for key, value in kwargs.items():
            # check dataframe enter
            if key == "df":
                if not isinstance(value, pd.DataFrame):
                    raise TypeError("The column enter "
                                    "is not a dataframe.")
                else:
                    new_kwargs["df"] = value

            elif key == "column_to_test":
            # The name of column is stored in the attribute self.columns_to_test.
            # We want to obtain the name of each column in a list of column name.
                column_to_test = []
                column = value

                # if the user enters the Series
                if isinstance(column, pd.Series):
                    column_to_test.append(column.name)

                # to select all columns
                elif column == 'all':
                    column_to_test.extend(list(df.columns))

                # if the person enters the name of one column
                elif isinstance(column, str):
                    if column not in df.columns:
                        raise NameError("The column you enter is not in the dataframe.")
                    else:
                        column_to_test.append(column)

                # if the person enters the index of the column
                elif isinstance(column, int):
                    column_to_test.append(df.iloc[:, column].name)

                # if the person enters a list
                elif isinstance(column, list):

                    # There is three possibilities :
                    # * either it contains the name of the columns,
                    # * either it contains the pd.Series
                    # * either it contains a list of index

                    for column in column:
                        # If it's column
                        if isinstance(column, pd.Series):
                            column_to_test.append(column.name)

                        # If it's name, check its presence in the dataframe
                        elif isinstance(column, str):
                            if column not in df.columns:
                                raise NameError(f"The column \"{column}\" you enter "
                                                "is not in the dataframe")
                            else:
                                column_to_test.append(column)

                        # it is the index of column
                        elif isinstance(column, int):
                            column_to_test.append(df.iloc[:, column].name)

                else:
                    raise TypeError(f"The type of data {type(column)} "
                                "is not supported to refer column.")

                # Avoid potential duplicates
                column_to_test = list(set(column_to_test))
                new_kwargs["column_to_test"] = column_to_test

            elif key == "participant_column":
                
                pre_participant_column = value

                if isinstance(pre_participant_column, pd.Series):
                    participant_column = pre_participant_column.name

                elif isinstance(pre_participant_column, int):
                    participant_column = \
                        df.iloc[:, pre_participant_column].name

                elif isinstance(pre_participant_column, str):
                    if pre_participant_column not in df.columns:
                        raise NameError("The column you enter is not in the dataframe")
                    else:
                        participant_column = pre_participant_column
                else:
                    raise TypeError(f"The type of data {type(column)} "
                                "is not supported to refer column.")
                
                # avoid potential overlap between column to test and participant column
                if pre_participant_column in column_to_test:
                    raise ValueError("The participant column can't "
                                    "be in the columns you want to test")
                new_kwargs["participant_column"] = participant_column
            
            elif key == "distance":
                pre_distance = value
                try:
                    distance = float(str(value).replace(r"\.", ","))
                except ValueError:
                    raise ValueError("You need to enter a numeric "
                                     "(a float or an integer) distance.")
                new_kwargs["distance"] = distance
        
        # to allow to pass self for class
        if "self" in kwargs.keys():
            func = function(kwargs["self"], **new_kwargs)
        else:
            func = function(**new_kwargs)
        return func
    return select_columns_to_test

class Outliers:
    """
    Contains the information about the different outliers
    for a certain column or list of columns
    :param dataframe: The dataframe used
    :param column: The column that the user wants to test.
    """
    @check
    def __init__(
            self,
            df: pd.DataFrame,
            column_to_test: str | list | int | pd.Series,
            participant_column: str | int | pd.Series,
            ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column

    def __check_if_numeric(self):
        not_numeric = []
        for column in self.columns_to_test:
            # TODOOOOOOOOOOOOOOOOOOOOooooooo
            try:
                pass
            except:
                pass
            if not is_numeric_dtype(column):
                not_numeric.append(column)
        print(not_numeric)
        if len(not_numeric) > 0:
            # raise TypeError(f"{not_numeric} is not numeric.
            # Thus, the outlier detection wont be possible.")
            pass

        self.columns_to_test = list(set(self.columns_to_test)
                                    - set(not_numeric))

    @staticmethod
    def convert_numeric():
        pass

    @staticmethod
    def outliers_iqr(self, distance):
        distance, error = self.verify_distance(distance)

        if error:
            return (0)

        for column in self.columns_to_test:
            # Calculate threshold
            low_threshold, high_threshold = calculate_iqr(
                self.df, column, distance
                )
            # list of outliers by column
            list_outliers = self.df.index[
                ((self.df[column] < low_threshold)
                 (self.df[column] > high_threshold))
                ].tolist()

@check
def calculate_iqr(
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
        column: str
            The name of the colum of interest
        distance: float
    """
    # calculate the interquartile range and the median
    ret = {}
    for column in column_to_test:
        print("*"*20, column, type(column))
        print(df.head())
        q1, q3 = df[column].quantile([0.25, 0.75])
        iqr = q3-q1

        med = np.median(df[column])

        # threshold
        low_threshold = med - (distance * iqr)
        high_threshold = med + (distance * iqr)
        ret[column] = (low_threshold, high_threshold)

    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret


if __name__ == "__main__":
    df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    print(df.columns)
    #low_threshold, high_threshold = calculate_iqr(df, ["premiere_lettre_nombre"], 2)
    outliers = Outliers(df=df, column_to_test="premiere_lettre_nombre", participant_column="LIB_NOM_PAT_IND_TPW_IND")
    # print(outliers.columns_to_test)
