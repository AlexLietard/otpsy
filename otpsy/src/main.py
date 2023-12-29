from otpsy.src import utils
from otpsy.src import config
from otpsy.src.visualise import app

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
            **kwargs
    ) -> None:

        self.columns_to_test = column_to_test
        self.participant_column = participant_column
        if self.participant_column == "":
            self.df = df
        else:
            self.df = df.set_index(self.participant_column)

        if "missing" in kwargs:
            self.missing = kwargs["missing"]
        else:
            self.missing = "No additional missing values"
    
    def visualise(self, column=""):
        if column == "":
            column_to_vis = self.columns_to_test
        else:
            column_to_vis = utils._process_column_to_test(self.df, column)
        app.main(self.df, column_to_vis)

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

    The Outliers class contains all the common method of the children classes.
    Children classes are all outliers class (SD, IQR,...).
    """

    def __str__(self):
        output_text = "-"*30
        output_text += "\nSummary of the outliers detection\n"
        output_text += "-"*30
        output_text += "\n\n"

        if self.multi == True:
            output_text += utils.header_add_true(self)
            output_text += utils.content_add_true(self)

        else:
            output_text += utils.header_add_false(self)
            output_text += utils.content_add_false(self)
        return output_text[0:-2]

    def concat(self, obj_to_merge):
        
        # see it is useful
        if not isinstance(self, MethodMulti):
            new_obj = MethodMulti(self.df)
        else:
            new_obj = self
        # Update paramaters like method if this is an outliers object
        if issubclass(type(obj_to_merge), _Outliers):
            new_obj.dict_col = dic_ini

            # Update all parameters for __str__ output
            if self.multi == False:  # if this is the first addition
                # method
                new_obj.method = [self.method]

                # distance
                new_obj.distance = {self.distance: [self.dimin]}

                # short name
                new_obj.dimin.extend([self.dimin, obj_to_merge.dimin])

                # column associated with method
                for column in self.columns_to_test:
                    new_obj.columns_to_test_w_method[column] = [
                        str(self.dimin)]
                    new_obj.threshold[column] = {
                        self.dimin: self.threshold[column]}

            # Add the element about o (the other object)
            new_obj.method.append(obj_to_merge.method)
            if obj_to_merge.distance not in new_obj.distance:
                new_obj.distance[obj_to_merge.distance] = [obj_to_merge.dimin]
            else:
                new_obj.distance[obj_to_merge.distance].append(obj_to_merge.dimin)

            # for each column in the object to add
            for column in obj_to_merge.columns_to_test:
                if column in self.columns_to_test:
                    new_obj.columns_to_test_w_method[column].append(obj_to_merge.dimin)
                    new_obj.threshold[column][obj_to_merge.dimin] = obj_to_merge.threshold[column]
                else:
                    new_obj.columns_to_test_w_method[column] = [obj_to_merge.dimin]
                    if obj_to_merge.dimin == "cut-off":
                        new_obj.threshold[column] = {obj_to_merge.dimin: obj_to_merge.threshold}
                    else:
                        new_obj.threshold[column] = {
                            obj_to_merge.dimin: obj_to_merge.threshold[column]}

            # Add column to test associated with columns to test
            new_obj.columns_to_test = list(
                set(self.columns_to_test + obj_to_merge.columns_to_test))

            # Add number of outliers associated to a specific column and
            # avoid duplicate in outliers
            for column in new_obj.columns_to_test:
                new_obj.dict_col[column] = list(set(
                    new_obj.dict_col[column]
                ))
                new_obj.nb[column] = len(new_obj.dict_col[column])
        return MethodMulti()

    def add(self, list_to_merge):
        """
        The addition of outliers to the existing object.

        If the object being added is another outliers object,
        it returns a new object, specifically a multi-outliers object.
        Otherwise, it returns the same object with an additional
        section labeled 'Added manually', 
        or "added_manually" on the dataframe.
        """

        # If User input : out_obj.add("participant1")
        if isinstance(list_to_merge, (str)):
            list_to_merge = [list_to_merge]
        
        # User input out_obj.add(["participant1", "participant2"]) or
        # string transform to list
        if isinstance(list_to_merge, (list)):
            # if there is already a column added_manually coming from
            # a past addition, it extends it. If not, it create a new
            # key that have the value []. 
            # The comprehension list is to avoid redundancy
            self.dict_col.setdefault("added_manually", []).extend(
                [elem for elem in list_to_merge 
                 if elem not in self.dict_col["added_manually"]])
            
            # Update other parameters
            self.nb["added_manually"] = len(self.dict_col["added_manually"])
            self.position["added_manually"] = utils._get_position(
                self.df, self.dict_col)
            self.all_index = utils._select_index(
                self.dict_col.keys(), self.dict_col)
        
        elif issubclass(type(list_to_merge), _Outliers):
            raise KeyError('You can\'t add an outlier object'
                            ' with this method. \n'
                            'You can use ot.concat(out1, out2)')

        return self

    def __sub__(self, o):
        """
        This method allows to substract remove outliers from the object. 
        For example, if you detect outliers through a specific method,
        you can judge that the participant X is not outliers and remove
        him from the outliers. 
        """ 
        dic_ini = self.dict_col
        try:
            # User inputed something like
            # Out_obj - ["participant1", "participant2"]
            if isinstance(o, list):
                for column in dic_ini:
                    o_str = [str(value) for value in o]
                    dic_ini[column] = [value for value in dic_ini[column]
                                       if str(value) not in o_str]
            # User inputed something like
            # Out_obj - {"first_column": ["participant1", "participant2"]}
            elif isinstance(o, dict):
                for column in o:
                    # transform to a list for allow iteration if user input :
                    # Out_obj - {"first_column": "participant1"}
                    if isinstance(o[column], (int, str)):
                        o[column] = [o[column]]
                    o[column] = [str(value) for value in o[column]]
                    dic_ini[column] = [value for value in dic_ini[column]
                                       if str(value) not in o[column]]
            # If there is just one participant index 
            # User inputed : Out_obj - "participant1"
            elif isinstance(o, (int, str)):
                for column in dic_ini:
                    dic_ini[column] = [value for value in dic_ini[column]
                                       if str(value) != str(o)]
        except KeyError as key:
            raise KeyError(f'It seems that the column {column} '
                           'added is not present in the outliers'
                           ' object') from key
        except TypeError as type:
            raise TypeError("This type of value is not "
                            "supported.") from type

        self.dict_col = dic_ini
        for column in self.columns_to_test:
            self.dict_col[column] = list(set(
                self.dict_col[column]
            ))
            self.nb[column] = len(self.dict_col[column])

        return self

    def _calculate(self, method):
        """ Private method used to calculate outliers """
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        # As there is no constructor, this attribute has the purpose.
        # If the user use the method __add__, add take the value True.
        # This attribute is used in the method __str__.
        self.multi = False
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
        self.dimin = "iqr"
        self._calculate(self.dimin)


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
        self.dimin = "sd"
        self._calculate(self.dimin)


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
        self.dimin = "rsd"
        self._calculate(self.dimin)

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
        self.dimin = "mad"
        self._calculate(self.dimin)


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
        self.dimin = "tukey"
        self._calculate(self.dimin)


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
        self.dimin = "sn"
        self._calculate(self.dimin)

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
        self.dimin = "prctile"
        self._calculate(self.dimin)


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
        self.distance = threshold
        self.threshold = threshold
        self.method = "Cut-Off"
        self.dimin = "cut-off"
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
        self.dimin = "id"
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
            self.df, self.dict_col, self.dimin)

    def __str__(self):
        output_text = utils.header_add_false(self)
        output_text += f"There is {self.nb} participant with a frequency" \
                       f" above {self.frequency} : "

        if self.nb > 0 and self.nb <= 5:
            output_text += ", ".join([str(val)
                                      for val in self.dict_col])

        elif self.nb > 5:
            output_text += str(self.dict_col[0]) + ", " + \
                str(self.dict_col[1]) \
                + "."*5 + ", " + \
                str(self.dict_col[-1])
        else:  # if there is no outliers
            output_text = output_text[0:-3] + "."  # take out last ":"
        return output_text[0:-2]


class MethodMulti(_Outliers):
    def __init__(self, df):
        self.df = df
        self.method = []
        self.distance = {}
        self.nb = {}
        self.threshold = {}
        self.columns_to_test = []
        self.columns_to_test_w_method = {}
        self.multi = True
        self.dimin = []

