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
            participant_column: str | int | pd.Series = "",
    ) -> None:

        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        if self.participant_column != "":
            self.df = df.set_index(self.participant_column)
        else:
            self.df = df

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

    def method_prctile(self, distance):
        return MethodPrctile(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )


class Outliers:
    """ Parent class of every outliers class

    The Outliers class contains all the common method of the child class
    associated to each outlier method.
    """

    def __str__(self):
        output_text = "-"*30
        output_text += "\nSummary of the outliers detection\n"
        output_text += "-"*30
        output_text += "\n\n"
        output_text += f"Method used : {self.method}\n"
        output_text += f"Distance used : {self.distance}\n"
        output_text += f"Column tested : {', '.join(self.columns_to_test)}\n" \
            + "-"*30 + "\n"
        for column in self.columns_to_test:
            output_text += f"The column {column} has " \
                           f"{self.outliers_nb[column]} outliers : "
            if self.outliers_nb[column] > 0:
                output_text += str(self.outliers[column][0]) + ", " + \
                    str(self.outliers[column][1]) \
                    + "."*5 + ", " + \
                    str(self.outliers[column][-1])
            if self.method == "Sn":
                output_text += "\nThe threshold median distance to other " \
                    f"point is {round(self.threshold[column], 2)} \n\n"
            else:
                output_text += "\nThe low threshold is " \
                    f"{round(self.threshold[column][0], 2)} and "\
                    f"the high threshold is {round(self.threshold[column][1], 2)}\n\n"
        return output_text[0:-2]

    def _calculate(self, method):
        self.outliers = {}
        self.threshold = {}
        self.outliers_nb = {}
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
            self.outliers_nb[column] = len(list_outliers)

    def _select_index_for_deletion(self, column_to_keep):
        index_to_delete = [
            index for key, value in self.outliers.items()
            for index in value if key in column_to_keep
        ]
        return list(set(index_to_delete))

    def manage(self, method="delete", column=None):
        """
        You can manage your outliers using different methods:
        * delete : delete the row if it contains 1 or more outliers
        value
        * na : replace all outliers by missing value
        * winsorise : replace outliers by threshold value obtain through
        the outlier method used.
        """
        if column is None:
            column = self.columns_to_test
        # to allow modification of the dataframe without changing the
        # attribute of the object, a new dataframe is created
        new_df = self.df
        column_to_keep = [col for col in self.columns_to_test if col in column]

        if method == "delete":
            index_to_delete_clean = self._select_index_for_deletion(
                column_to_keep)
            final_df = new_df.drop(index_to_delete_clean)

        elif method == "na":
            for column in column_to_keep:
                new_df.loc[self.outliers[column], column] = np.nan
            final_df = new_df

        elif method == "winsorise":
            if self.method == "Sn":
                raise ValueError("No winsorisation is "
                                 "possible with the Sn method")
            for column in column_to_keep:
                low_threshold, high_threshold = self.threshold[column]
                new_df.loc[new_df[column] <
                           low_threshold, column] = low_threshold
                new_df.loc[new_df[column] > high_threshold,
                           column] = high_threshold
            final_df = new_df

        return final_df


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
        self.method = "Inter-quartile range"
        self._calculate("iqr")


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
        self.method = "Standard Deviation"
        self._calculate("sd")


class MethodRSd(Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float,
        max_iteration: int,
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.max_iteration = max_iteration
        self.method = "Recursive Standard Deviation"
        self._calculate("rsd")

    def _calculate(self, method):
        self.outliers = {}
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:

            df_to_operate_n = pd.DataFrame()
            df_to_operate_n_plus_1 = self.df
            self.iteration = 0

            while len(df_to_operate_n.index) \
                != len(df_to_operate_n_plus_1.index) \
                    and self.iteration < self.max_iteration:

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
                df_to_operate_n_plus_1 = df_to_operate_n.drop(
                    labels=list_outliers,
                    axis=0,
                    errors="ignore"
                )
                self.iteration += 1


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
        self.method = "Median Absolute Distance"
        self._calculate("mad")


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
        self.method = "Tukey"
        self._calculate("tukey")


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
        self.method = "Sn"
        self._calculate("sn")

    def _calculate(self, method):
        self.outliers = {}
        self.threshold = {}
        self.outliers_nb = {}
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
            self.threshold[column] = threshold
            self.outliers_nb[column] = len(list_outliers)


class MethodPrctile(Outliers):
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
        self.method = "Percentile"
        self._calculate("prctile")


if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    outliers = Sample(df_test,
                      column_to_test=["CLI1", "PAT1"],
                      ).method_Sn(2.5)
    print(outliers)
