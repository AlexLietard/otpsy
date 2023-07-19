from inspect import signature
from warnings import warn
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_float_dtype
import numpy as np


def _process_column_to_test(df_func, pre_column):
    """This function aim to process the keyword argument column to test"""

    # The name of column is stored in the attribute self.columns_to_test.
    # We want to obtain the name of each column in a list of column name.
    column_to_test = []

    # if the user enters the Series
    if isinstance(pre_column, pd.Series):
        column_to_test.append(pre_column.name)

    # to select all columns
    elif pre_column == 'all':
        column_to_test.extend(list(df_func.columns))

    # if the person enters the name of one column
    elif isinstance(pre_column, str):
        if pre_column not in df_func.columns:
            raise NameError("The column you enter is not in the dataframe.")
        column_to_test.append(pre_column)

    # if the person enters the index of the column
    elif isinstance(pre_column, int):
        column_to_test.append(df_func.iloc[:, pre_column].name)

    # if the person enters a list
    elif isinstance(pre_column, list):

        # There is three possibilities :
        # * either it contains the name of the columns,
        # * either it contains the pd.Series
        # * either it contains a list of index

        for col in pre_column:
            # If it's column
            if isinstance(col, pd.Series):
                column_to_test.append(col.name)

            # If it's name, check its presence in the dataframe
            elif isinstance(col, str):
                if col not in df_func.columns:
                    raise NameError(f"The column \"{col}\" you enter "
                                    "is not in the dataframe")
                column_to_test.append(col)

            # it is the index of column
            elif isinstance(pre_column, int):
                column_to_test.append(df_func.iloc[:, col].name)
    # Avoid potential duplicates
    else:
        raise TypeError(f"The type of data {type(pre_column)} "
                    "is not supported to refer column.")
    return list(set(column_to_test))

def _process_participant_column(df_func, pre_participant_column):
    """ Process the participant column to obtain the name
    """
    if isinstance(pre_participant_column, pd.Series):
        participant_column = pre_participant_column.name

    elif isinstance(pre_participant_column, int):
        participant_column = \
            df_func.iloc[:, pre_participant_column].name

    elif isinstance(pre_participant_column, str):
        if pre_participant_column not in df_func.columns:
            raise NameError("The column you enter is not in the dataframe")
        participant_column = pre_participant_column
    else:
        raise TypeError(f"The type of data {type(pre_participant_column)} "
                         "is not supported to refer column.")
    return participant_column

def _convert_column_to_numeric(df_func, column_to_test_func):
    """
    to convert column in a numeric format
    """
    # Before and after modifying are present to track
    # the number of missing values. This information
    # will be use to give a feedback to the user.

    columns_modified = []
    before_transforming = df_func.isna().sum().sum()

    # convert each column that is not a float
    # or integer
    for column in column_to_test_func:
        if not is_float_dtype(df_func[column]) or not \
            is_numeric_dtype(df_func[column]):
            df_func[column] = pd.to_numeric(
                df_func[column].astype(str).\
                str.replace(",", "."), errors='coerce')
        columns_modified.append(column)

    after_transforming = df_func.isna().sum().sum()

    if len(columns_modified)>0 and before_transforming < after_transforming:
        warn(f"Columns {columns_modified} has "
                "been modified because they were "
                "not numeric. When it was not "
                "convertible to numeric, it gave "
                "missing value. The number of missing "
                f"value went from {before_transforming} "
                f"to {after_transforming}.")


def check(function):
    """ Decorator to transform argument in the good format

    For every parameters possible in the package, there is
    a check of the arguments passed.  
    """
    def verify_arguments(*args, **kwargs):
        new_kwargs = {}

        # to associate the argument from args to the
        # keyword to have only kwargs
        kwargs = signature(function).bind(*args, **kwargs).arguments

        for key, value in kwargs.items():
            # check dataframe enter
            if key == "df":
                if not isinstance(value, pd.DataFrame):
                    raise TypeError("The argument entered for df"
                                    "is not a dataframe.")
                new_kwargs["df"] = value
                df = value

            # check column to test
            elif key == "column_to_test":
                pre_column = value
                column_to_test = _process_column_to_test(df, pre_column)
                _convert_column_to_numeric(df, column_to_test)
                new_kwargs["column_to_test"] = column_to_test


            # check participant column
            elif key == "participant_column":

                pre_participant_column = value

                participant_column = _process_participant_column(
                    df, pre_participant_column)
                # avoid potential overlap between column to test and participant column
                if participant_column in column_to_test:
                    raise ValueError("The participant column can't "
                                    "be in the columns you want to test")
                new_kwargs["participant_column"] = participant_column

            # check distance
            elif key == "distance":
                try:
                    distance = float(str(value).replace(r"\.", ","))
                    print(distance)
                except ValueError:
                    raise ValueError("You need to enter a numeric "
                                     "(a float or an integer) distance.") \
                                            from ValueError
                new_kwargs["distance"] = distance

        # to pass self when its decorating class
        if "self" in kwargs:
            func = function(kwargs["self"], **new_kwargs)
        else:
            func = function(**new_kwargs)
        return func

    return verify_arguments

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
            low_threshold, high_threshold = threshold_iqr(
                self.df, column, distance
                )
            # list of outliers by column
            list_outliers = self.df.index[
                ((self.df[column] < low_threshold)
                 (self.df[column] > high_threshold))
                ].tolist()

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

    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret


if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    low, high = threshold_iqr(df_test, ["CLI1"], 2)
    print(low, high)
    # outliers = Outliers(df, "premiere_lettre_nombre", "LIB_NOM_PAT_IND_TPW_IND")
    # print(outliers.columns_to_test)
