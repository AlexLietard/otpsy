import utils
import config
import pandas as pd
import numpy as np


class Sample:
    """
    Contains the data you want to pass in the detection
    of outliers.
    Parameters
        * df (pd.Dataframe) :
            * Enter the dataframe you want to test
        * column_to_test (str | list | int | pd.Series) :
            * Enter either the name, a list of name,
            the index of column, or directly the column
        * participant_column: str | int | pd.Series
            * Enter the participant refering participant. 
            If this column is directly your index, or you want
            to see the line number of outliers, don't specify a
            arguments. 
    """
    @utils.check_Sample
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

    @utils.check_number_entry
    def method_IQR(self, distance):
        """fonction pour ken"""
        return MethodIqr(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_SD(self, distance):
        return MethodSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_rSD(self, distance, iteration):
        return MethodRSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            iteration
        )

    @utils.check_number_entry
    def method_MAD(self, distance):
        return MethodMad(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_Tukey(self, distance):
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_Sn(self, distance):
        return MethodSn(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_prctile(self, distance):
        return MethodPrctile(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_cutoff(self, threshold):
        return MethodCutOff(
            self.df,
            self.columns_to_test,
            self.participant_column,
            threshold
        )

    @utils.check_number_entry
    def method_identical(self, frequency):
        return MethodIdentical(
            self.df,
            self.columns_to_test,
            self.participant_column,
            frequency
        )


class _Outliers:
    """ ! Private Parent class of every outliers class !

    The Outliers class contains all the common method of the child class.
    Child class are all outliers class (SD, IQR,...). 
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
                output_text += "\nThreshold median distance to other " \
                    f"point is {round(self.threshold[column], 2)} \n\n"
            else:
                output_text += "\nLow threshold : " \
                    f"{round(self.threshold[column][0], 2)} / "\
                    f"High threshold : {round(self.threshold[column][1], 2)}"\
                    "\n\n"
        return output_text[0:-2]

    def _calculate(self, method):
        """ Private method used to calculate outliers """
        self.outliers_index = {}
        self.outliers = {}
        self.threshold = {}
        self.outliers_nb = {}
        # get the function for calculate threshold
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:
            # Calculate threshold
            low_threshold, high_threshold = func(
                self.df, [column], self.distance)
            # list of outliers by column
            list_outliers = self.df.index[
                ((self.df[column] < low_threshold) |
                 (self.df[column] > high_threshold))
            ].tolist()
            self.outliers[column] = list_outliers
            self.threshold[column] = (low_threshold, high_threshold)
            self.outliers_nb[column] = len(list_outliers)
        self.outliers_index = utils._select_index(
            self.outliers.keys(), self.outliers)

    @utils.check_Sample
    def manage(self, method="delete", column=None):
        """ Manage your outliers

        After detecting outliers, you can deal with them using 
        different methods. The method you will apply can be applied
        only on specific columns. 
        ---
        Parameters
            * method (str): You can manage your outliers using different methods :
                * delete : delete the row if it contains 1 or more outliers
                value, also call truncation
                * na : replace all outliers by missing value NaN
                * winsorise : replace outliers by threshold value obtain through
                the outlier method used.
            * column (str|list|pd.Series|int) : Reference specific columns 
            if you want to apply to manage only on them.
        """
        if column is None:
            column = self.columns_to_test
        # to allow modification of the dataframe without changing the
        # attribute of the object, a new dataframe is created
        new_df = self.df
        column_to_keep = [col for col in self.columns_to_test if col in column]

        if method == "delete":
            index_to_delete_clean = utils._select_index(
                column_to_keep, self.outliers)
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

    def inspect(
            self,
            aberrant: str = "value",
            other_value: str = "bool",
            all_participants: bool = False,
            all_columns: bool = False,
    ):
        """ Inspect in more details your outlier

        This method has the purpose to show some details about the outliers.
        It renders a table containing all outliers, editable via parameters 
        of the function.
        ---
        Parameters:
            * aberrant (str) : Format of aberrant value
                * value (default value) : If an outlier value is detected,
                then the cell will contains the value of this one.
                * bool : If an outlier value is detected, then the cell
                will contains the boolean True
            * other_value (str) : Format of other value
                * bool (default value): If the value is not aberrant,
                then the cell will contains the boolean cell.
                * value : If the value is not aberrant, then the cell
                will contains the value associated
            * all_participants (bool) : Keep all participant or not
                * False (default value) : Participants without aberrant value
                is not present in the table.
                * True : Participant without aberrant value is present
            * all_columns (bool) : Keep all columns or not
                * False (default value) : The table only contains columns
                that has been chosen to test. Thus, if your initial dataframe
                contains 20 columns and you choose to test 5 of them, the
                final table will contains 5 columns
                * True : The table contains every columns in the initial
                dataframe. Thus, if your initial dataframe contains 20
                columns and you tested only 5 of them, the final table
                will contains 20 columns.
        """
        table = pd.DataFrame(index=self.df.index)
        # the iteration on df.columns and not on keys of self.outliers
        # is present to conserve the order of columns in the initial
        # dataframe
        for column in self.df.columns:
            if column in self.outliers:
                temporary_series = self.df[[column]].apply(
                    utils._parameters_of_the_table,
                    args=(aberrant, other_value, self.outliers, column),
                    axis=1)
                df_to_append = pd.DataFrame(temporary_series, columns=[column])
                table = table.join(df_to_append)
            else:
                table[column] = self.df[column]
        if not all_participants:
            table = table.loc[table.index.isin(
                self.outliers_index)]
        if not all_columns:
            table = table[self.outliers.keys()]
        return table


class MethodIqr(_Outliers):
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


class MethodSd(_Outliers):
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


class MethodRSd(_Outliers):
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
        self.outliers_index = {}
        self.outliers = {}
        self.threshold = {}
        self.outliers_nb = {}
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
                    df_to_operate_n_plus_1, [column], self.distance)
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
            self.threshold[column] = (low_threshold, high_threshold)
            self.outliers_nb[column] = len(list_outliers)
            self.outliers_index = utils._select_index(
                self.outliers.keys(), self.outliers)


class MethodMad(_Outliers):
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


class MethodTukey(_Outliers):
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


class MethodSn(_Outliers):
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
                self.df, [column], self.distance)
            # list of outliers by column
            # Contrary to the parent calculate method,
            # the identification is realised on the all_distance
            # which contains every median distance to other point
            list_outliers = all_distance.index[
                all_distance > threshold
            ].tolist()
            self.outliers[column] = list_outliers
            self.threshold[column] = threshold
            self.outliers_nb[column] = len(list_outliers)


class MethodPrctile(_Outliers):
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


class MethodCutOff(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        threshold: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.threshold = threshold
        self.method = "Cut-Off"
        self._calculate()

    def _calculate(self):
        """ Private method used to calculate outliers """
        self.outliers_index = {}
        self.outliers = {}
        self.outliers_nb = {}
        # get the function for calculate threshold
        for column in self.columns_to_test:
            # list of outliers by column
            list_outliers = self.df.index[
                self.df[column] < self.threshold
            ].tolist()
            self.outliers[column] = list_outliers
            self.outliers_nb[column] = len(list_outliers)
        self.outliers_index = utils._select_index(
            self.outliers.keys(), self.outliers)


class MethodIdentical(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        frequency: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.frequency = frequency
        self.method = "Identical"
        self._calculate("identical")
        
    def _calculate(self, method):
        """ Private method used to calculate outliers """
        self.outliers_index = {}
        self.outliers = {}
        self.threshold = {}
        self.outliers_nb = {}
        # get the function for calculate threshold
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:
            # Calculate threshold
            max_frequency = func(
                self.df, [column])
            # list of outliers by column
            '''list_outliers = self.df.index[
                ((self.df[column] < low_threshold) |
                 (self.df[column] > high_threshold))
            ].tolist()
            self.outliers[column] = list_outliers
            self.threshold[column] = (low_threshold, high_threshold)
            self.outliers_nb[column] = len(list_outliers)
        self.outliers_index = utils._select_index(
            self.outliers.keys(), self.outliers)'''



if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    outliers = Sample(df_test,
                      column_to_test=["CLI1", "PAT1"],
                      participant_column="LIB_NOM_PAT_IND_TPW_IND"
                      ).method_identical(80)
    inspection = outliers.inspect(all_columns=True)
    print(inspection)
