import pandas as pd
import numpy as np
from utils import check
import config


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

    def method_iqr(self, distance):
        """fonction pour ken"""
        return MethodIqr(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_sd(self, distance):
        return MethodSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_mad(self, distance):
        return MethodMad(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_tukey(self, distance):
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_Sn(self, distance):
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )


class Outliers:
    def calculate(self, method):
        self.outliers = {}
        func = config.DICT_FUNCTION.get(method)
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


class MethodIqr(Outliers):
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


class MethodSd(Outliers):
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
        self.calculate("sd")


class MethodMad(Outliers):
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
        self.calculate("mad")


class MethodTukey(Outliers):
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
        self.calculate("tukey")

class MethodSn(Outliers):
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
        self.calculate("Sn")

    def calculate(self, method):
        self.outliers = {}
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:
            # Calculate threshold
            low_threshold, high_threshold, all_median = func(
                self.df, column, self.distance)
            # list of outliers by column
            # Contrary to the parent calculate method
            # the identification is realised on the all_median
            # which contains every median distance to other point
            list_outliers = all_median.index[
                ((all_median[column] < low_threshold) |
                 (all_median[column] > high_threshold))
            ].tolist()
            self.outliers[column] = list_outliers

if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    outliers = Sample(df_test, ["PAT1", "CLI1", "DIF1"],
                      "LIB_NOM_PAT_IND_TPW_IND").method_Sn(1.5)
    print(outliers)
