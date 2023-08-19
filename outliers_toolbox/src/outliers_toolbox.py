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
            column_to_test: str | list | int | pd.Series = "",
            participant_column: str | int | pd.Series = "",
    ) -> None:

        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.df = df.set_index(self.participant_column)

    def method_IQR(self, distance):
        """fonction pour ken"""
        return MethodIqr(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_SD(self, distance):
        return MethodSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_rSD(self, distance, iteration):
        return MethodRSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            iteration
        )

    def method_MAD(self, distance):
        return MethodMad(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_Tukey(self, distance):
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    def method_Sn(self, distance):
        return MethodSn(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )


class Outliers:
    def calculate(self, method):
        self.outliers = {}
        self.threshold = {}
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
            self.threshold[column] = (low_threshold, high_threshold)

    def __str__(self):
        return str(self.outliers)

    def manage(self, method="delete", column=None):
        """
        You can manage your outliers using different methods:
        * delete : delete the row if it contains 1 or more outliers
        value
        * na : replace all outliers value by missing one
        * winsorise : replace outliers by threshold value of the method
        """
        if column is None:
            column = self.column_to_test
        # to allow modification of the dataframe without changing the
        # attribute of the object, a new dataframe is created
        new_df = self.df
        column_to_keep = [col for col in self.column_to_test if col in column]
        if method == "delete":
            index_to_delete_clean = self._select_index_for_deletion(column)
            final_df = new_df.drop(index_to_delete_clean)
        elif method == "na":
            for col in column_to_keep:
                new_df.loc[self.outliers[col], col] = np.nan
            final_df = new_df
        elif method == "winsorise":
            for col in column_to_keep:
                low_threshold, high_threshold = self.threshold[col]
                new_df.loc[new_df[col] < low_threshold, col] = low_threshold
                new_df.loc[new_df[col] > high_threshold, col] = high_threshold
            final_df = new_df
        return final_df

    def _select_index_for_deletion(self, column):
        index_to_delete = [
            index for key, value in self.outliers.items()
            for index in value if key in column_to_keep
        ]
        return list(set(index_to_delete))


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


class MethodRSd(Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float,
        iteration: int,
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.iteration = iteration
        self.calculate("rsd")

    def calculate(self, method):
        self.outliers = {}
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:

            df_to_operate_n = pd.DataFrame()
            df_to_operate_n_plus_1 = self.df
            n = 0

            while len(df_to_operate_n.index) \
                != len(df_to_operate_n_plus_1.index) \
                    and n < self.iteration:

                df_to_operate_n = df_to_operate_n_plus_1

                # Calculate threshold
                low_threshold, high_threshold = func(
                    df_to_operate_n_plus_1, column, self.distance)
                # list of outliers by column
                list_outliers = self.df.index[
                    ((self.df[column] < low_threshold) |
                     (self.df[column] > high_threshold))
                ].tolist()
                self.outliers[column] = list_outliers
                print(df_to_operate_n.index)
                df_to_operate_n_plus_1 = df_to_operate_n.drop(
                    labels=list_outliers,
                    axis=0,
                    errors="ignore"
                )
                n += 1


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
        self.calculate("sn")

    def calculate(self, method):
        self.outliers = {}
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:
            # Calculate threshold
            threshold, all_distance = func(
                self.df, column, self.distance)
            # list of outliers by column
            # Contrary to the parent calculate method
            # the identification is realised on the all_median
            # which contains every median distance to other point
            list_outliers = all_distance.index[
                all_distance > threshold
            ].tolist()
            self.outliers[column] = list_outliers


if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    outliers = Sample(df_test,
                      column_to_test=["CLI1"],
                      participant_column="LIB_NOM_PAT_IND_TPW_IND"
                      ).method_SD(3)
    print(outliers)
