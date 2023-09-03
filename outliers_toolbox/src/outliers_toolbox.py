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
    @utils.check_sample
    def __init__(
            self,
            df: pd.DataFrame,
            column_to_test: str | list | int | pd.Series = "",
            participant_column: str | int | pd.Series = "",
            ignore: bool = False,
            **kwargs
    ) -> None:

        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        if self.participant_column != "":
            self.df = df.set_index(self.participant_column)
        else:
            self.df = df

        if "missing" in kwargs:
            self.missing = kwargs["missing"]
        else:
            self.missing = "No additional missing values"

    @utils.check_number_entry
    def method_IQR(self, distance=2):
        return MethodIqr(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_SD(self, distance=2.5):
        return MethodSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_rSD(self, distance=3, iteration=50):
        return MethodRSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            iteration
        )

    @utils.check_number_entry
    def method_MAD(self, distance=2.5, b=1.4826):
        return MethodMad(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            b
        )

    @utils.check_number_entry
    def method_Tukey(self, distance=1.5):
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_Sn(self, distance=3):
        return MethodSn(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_prctile(self, distance=0.95):
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
    def method_identical(self, frequency=0.98):
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
                           f"{self.nb[column]} outliers : "

            if self.nb[column] > 0 and self.nb[column] <= 5:
                output_text += str(", ".join(self.dict_col[column]))
            elif self.nb[column] > 5:
                output_text += str(self.dict_col[column][0]) + ", " + \
                    str(self.dict_col[column][1]) \
                    + "."*5 + ", " + \
                    str(self.dict_col[column][-1])
            else:  # if there is no outliers
                output_text = output_text[0:-3] + "."  # take out last ":"

            if self.method == "Sn":
                output_text += "\nThreshold median distance to other " \
                    f"point is {round(self.threshold[column], 2)} \n\n"
            else:
                output_text += "\nLow threshold : " \
                    f"{round(self.threshold[column][0], 2)} / "\
                    f"High threshold : {round(self.threshold[column][1], 2)}"\
                    "\n\n"
        return output_text[0:-2]

    def __add__(self, o):
        dic_ini = self.dict_col
        if isinstance(o, (dict, list)):
            dic_to_add = o
        else:
            try:
                dic_to_add = o.dict_col
            except AttributeError:
                raise ValueError("The addition need to be realised with"
                                 " a dictionnary or and outliers object")

        for column in dic_to_add:
            try:
                # even if this if else seems strange, it has a function
                # Indeed, if the participant enter a string, it is possible
                # to iterate on it, so we can't add a single string to it.
                # Thus I checked if its a string to append it now.
                if isinstance(dic_to_add[column], str):
                    dic_ini[column].append(dic_to_add[column])
                else:
                    dic_ini[column].extend(dic_to_add[column])

            except KeyError as key:
                raise KeyError(f'It seems that the column {column} '
                               'added is not present in the outliers'
                               ' object') from key
            except TypeError as e:
                if isinstance(dic_to_add[column], (int, float)):
                    dic_ini[column].append(dic_to_add[column])
                else:
                    raise TypeError("This type of value is not "
                                    "supported.") from e
        self.dict_col = dic_ini
        return self

    def __sub__(self, o):
        dic_ini = self.dict_col
        if isinstance(o, list):
            for column in dic_ini:
                o_str = [str(value) for value in o]
                dic_ini[column] = [value for value in dic_ini[column]
                                   if str(value) not in o_str]
        elif isinstance(o, dict):
            for column in o:
                if isinstance(o[column], (int, str)):
                    o[column] = [o[column]]
                o[column] = [str(value) for value in o[column]]
                dic_ini[column] = [value for value in dic_ini[column]
                                   if str(value) not in o[column]]

        elif isinstance(o, (int, str)):
            for column in dic_ini:
                dic_ini[column] = [value for value in dic_ini[column]
                                    if str(value) != str(o)]
        else:
            raise ValueError("The substraction need to be realised with"
                                 " a dictionnary or and outliers object")
        self.dict_col = dic_ini

        return self

    def _calculate(self, method):
        """ Private method used to calculate outliers """
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        # get the function for calculate threshold
        func = config.DICT_FUNCTION.get(method)
        for column in self.columns_to_test:
            # Calculate threshold
            # for the MAD method, a "b" can be given
            if method == "mad":
                low_threshold, high_threshold = func(
                    self.df, [column], self.distance, self.b)
            else:
                low_threshold, high_threshold = func(
                    self.df, [column], self.distance)

            # list of outliers by column
            list_outliers = self.df.index[
                ((self.df[column] < low_threshold) |
                 (self.df[column] > high_threshold))
            ].tolist()
            self.dict_col[column] = list_outliers
            self.threshold[column] = (low_threshold, high_threshold)
            self.nb[column] = len(list_outliers)
            self.position[column] = utils._get_position(
                self.df, self.dict_col)

        self.all_index = utils._select_index(
            self.dict_col.keys(), self.dict_col)

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
            if you want to apply the method manage only on them.
        """
        if column is None:
            column = self.columns_to_test
        # to allow modification of the dataframe without changing the
        # attribute of the object, a new dataframe is created
        new_df = self.df
        column_to_keep = [col for col in self.columns_to_test if col in column]

        if method == "delete":
            index_to_delete_clean = utils._select_index(
                column_to_keep, self.dict_col)
            final_df = new_df.drop(index_to_delete_clean)

        elif method == "na":
            for column in column_to_keep:
                new_df.loc[self.dict_col[column], column] = np.nan
            final_df = new_df

        elif method == "winsorise":
            if self.method == "Sn" or self.method == "Identical":
                raise ValueError('No winsorisation is '
                                 f'possible with the "{self.method}" method')
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
            if column in self.dict_col:
                temporary_series = self.df[[column]].apply(
                    utils._parameters_of_the_table,
                    args=(aberrant, other_value, self.dict_col, column),
                    axis=1)
                df_to_append = pd.DataFrame(temporary_series, columns=[column])
                table = table.join(df_to_append)
            else:
                table[column] = self.df[column]
        if not all_participants:
            table = table.loc[table.index.isin(
                self.all_index)]
        if not all_columns:
            table = table[self.dict_col.keys()]
        return table


class MethodIqr(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame | np.ndarray | pd.Series,
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
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
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

                self.dict_col[column] = list_outliers

                df_to_operate_n_plus_1 = df_to_operate_n.drop(
                    labels=list_outliers,
                    axis=0,
                    errors="ignore"
                )
                self.iteration += 1
            self.threshold[column] = (low_threshold, high_threshold)
            self.nb[column] = len(list_outliers)
            self.position[column] = utils._get_position(
                self.df, self.dict_col)
        self.all_index = utils._select_index(
            self.dict_col.keys(), self.dict_col)


class MethodMad(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float,
        b: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.b = b
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
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
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
            self.dict_col[column] = list_outliers
            self.threshold[column] = threshold
            self.nb[column] = len(list_outliers)
            self.position[column] = utils._get_position(
                self.df, self.dict_col)

        self.all_index = utils._select_index(
            self.dict_col.keys(), self.dict_col)


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
        self.all_index = {}
        self.dict_col = {}
        self.nb = {}
        self.position = {}
        # get the function for calculate threshold
        for column in self.columns_to_test:
            # list of outliers by column
            list_outliers = self.df.index[
                self.df[column] < self.threshold
            ].tolist()
            self.dict_col[column] = list_outliers
            self.nb[column] = len(list_outliers)
            self.position[column] = utils._get_position(
                self.df, self.dict_col)
        self.all_index = utils._select_index(
            self.dict_col.keys(), self.dict_col)


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
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        # get the function for calculate threshold
        func = config.DICT_FUNCTION.get(method)
        # Calculate threshold
        max_frequency = func(
            self.df, self.columns_to_test)
        # list of outliers by column
        list_outliers = self.df.index[
            (max_frequency > self.frequency)
        ].tolist()
        self.dict_col = list_outliers
        self.nb = len(list_outliers)
        self.all_index = list_outliers
        self.position = utils._get_position(
            self.df, self.dict_col)

    def __str__(self):
        return ", ".join(self.dict_col)


if __name__ == "__main__":
    df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
    df_outliers = df_test.drop(
        ["premiere_lettre", "LIB_NOM_PAT_IND_TPW_IND"], axis=1)
    sample = Sample(df_test,
                    column_to_test=["CLI1", "PAT1"])
    

    outliers = sample.method_IQR()
    print("Before: ", outliers.dict_col)
    bla = outliers - {"PAT1": [36, 89, 391]}
    print("After : ", bla.dict_col)
