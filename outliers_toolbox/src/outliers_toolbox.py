from inspect import signature
from warnings import warn
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_float_dtype
import numpy as np
from utils import check




class Sample:
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

        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.df = df.set_index(self.participant_column)

    def iqr_method(self, distance):
        return IqrMethod(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )


class Outliers:

    @staticmethod
    def _select_method(method):
        dict_function = {
            "iqr": threshold_iqr,
        }
        func = dict_function.get(method)
        return func

    def calculate(self, method):
        self.outliers = {}
        func = self._select_method(method)
        for column in self.columns_to_test:
            # Calculate threshold
            low_threshold, high_threshold = func(
                self.df, column, self.distance)
            # list of outliers by column
            list_outliers = self.df.index[
                ((self.df[column] < low_threshold) |
                 (self.df[column] > high_threshold))
            ].tolist()
            self.outliers[column] = list_outliers

    def __str__(self):
        return str(self.outliers)


class IqrMethod(Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.calculate("iqr")


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
            The distance used to calculate threshold
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

    # avoid having a dictionnary for one column
    if len(column_to_test) == 1:
        return ret[column_to_test[0]][0], ret[column_to_test[0]][1]
    else:
        return ret


if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    outliers = Sample(df_test, ["PAT1", "CLI1", "DIF1"],
                      "LIB_NOM_PAT_IND_TPW_IND").iqr_method(2)
    print(outliers)
