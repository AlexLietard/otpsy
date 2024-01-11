from otpsy.src import utils
from otpsy.src import config
from otpsy.src.visualise import app

import pandas as pd
import numpy as np


class Sample:
    """
    Enter a sample of your data on which you want to detect outliers.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to be processed. If you want to only test
        a series, you can enter a pd.Series. Other type of dataframe
        is still not supported.

    columns_to_test : str, list, int, or pd.Series, optional
        Columns to test corresponds to all columns you want
        to be considered for the outliers detection.
        Default is an empty string. If columns to test is an empty
        string or equals "all", then all thecolumns are considerer
        to be relevant.
        You can specify one column by specifying its name (str) or 
        his position (int).
        You can specify more than one column by enter a list of
        names (list[str]) or a list of position (list[index]).
        Using the name is preferable.
        ** IMPORTANTLY **, all columns are converted to numeric.
        If this conversion only led to missing values, it raises
        an error.
        If there is some missing values issued from this 
        conversion but not all, you can access all information via 
        `your_instance.missing`.

    participant_column : str, int, optional
        It corresponds to the column with the identifier of your 
        participant.
        This column is use as an index. Default is an empty 
        string. If participant_column equals to an empty string
        (default), the initial index of the dataframe will be keep.

    **kwargs
        Additional keyword arguments.

    Attributes
    ----------
    df : pd.DataFrame
        The processed DataFrame with the participant column set
        as the index, if specified.
    columns_to_test : str, list, int, or pd.Series
        Columns to test.
    participant_column : str, int
        The column used as an index.
    missing : str
        Information about additional missing values, defaults to
        "No additional missing values" if not provided.

    Notes
    -----
    The decorator @utils._check_sample allow to standardise arguments.
    As said before, access information about missing values with the
    attribute missing.

    Examples
    --------
    The fictitious dataframe is named "df". It includes notably the 3
    columns A, B, C and the column refering to participant index "ID".
    ```python
    >>> import otpsy as ot
    >>> # You want to test columns A, B, C
    >>> sample = ot.Sample(df, columns_to_test=["A", "B", "C"], 
    participant_column="ID")
    >>> # You want to specify with index
    >>> sample = ot.Sample(df, columns_to_test=[1, 2, 3], 
    participant_column=4)
    >>> # You only want to test one column
    >>> sample = ot.Sample(df, columns_to_test="A", 
    participant_column=4)
    >>> # You only want to test a series
    >>> sample = ot.Sample(df[["A"]])
    ```
    """
    @utils._check_sample
    def __init__(
            self,
            df: pd.DataFrame,
            columns_to_test: str | list[str] | int | list[int] | pd.Series = "",
            participant_column: str | int | pd.Series = "",
            **kwargs
        ) -> None:

        self.columns_to_test = columns_to_test
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

        return None

    @utils.check_number_entry
    def method_IQR(self, distance=2):
        """ ## Interquartile Range
        Method to create an outliers object via the **IQR-based** 
        outlier detection method. Distance refers to the number of 
        interquartile range above and below the median.

        Parameters
        ----------
        distance : int, optional
            The multiplier for the IQR to determine the 
            outlier thresholds.
            Default equals 2.

        Return
        -------
        MethodIqr: An instance of the MethodIqr class 
        containing the results of the outlier detection.
        """
        return MethodIqr(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_SD(self, distance=2.5):
        """## Standard Deviation
        Method to create an outliers object via the **SD-based** 
        outlier detection method. Distance refers to the number of 
        standard deviation above and below the mean.

        Parameters
        ----------
        distance : int, optional
            The multiplier for the SD to determine the 
            outlier thresholds.
            Default equals 2.5.

        Return
        -------
        MethodSd: An instance of the MethodSd class 
        containing the results of the outlier detection.
        """
        return MethodSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_rSD(self, distance=3, iteration=50):
        """ ## Recursive Standard Deviation
        Method to create an outliers object via the rSD-based outlier
        detection. The 'distance' parameter refers to the number of
        standard deviations above and below the mean at each iteration.
        In each iteration, outliers are flagged and removed from the
        column. Therefore, the detection of outliers is considered
        finished when the number of iterations equals the inputted
        number, or when no new outliers are found in an iteration.

        Parameters
        ----------
        distance : int, optional
            The multiplier for the IQR to determine the 
            outlier thresholds.
            Default equals 3.
        iteration : int, optional
            The number of maximum iteration. Default
            equals 50.

        Return
        -------
        MethodRSd: An instance of the MethodIqr class 
        containing the results of the outlier detection.
        """
        return MethodRSd(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            iteration
        )

    @utils.check_number_entry
    def method_MAD(self, distance=2.5, b=1.4826):
        """ ## Median Absolute Distance
        Method to create an outliers object via the median absolute
        distance outlier detection method. 
        The idea is that you realise calculate the difference between
        each point and the median, and you realise the median on this
        distance.
        The 'distance' parameter refers to the number of median absolute
        distance above and below the median.
        For more information with b, see Leys et al. (2013).

        Parameters
        ----------
        distance : int, optional
            The multiplier for the MAD to determine the 
            outlier thresholds.
            Default equals 2.5.
        b : int, optional
            Default equals 1.4826.

        Return
        -------
        MethodRSd: An instance of the MethodIqr class 
        containing the results of the outlier detection.
        """
        return MethodMad(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance,
            b
        )

    @utils.check_number_entry
    def method_Tukey(self, distance=1.5):
        """ ## Tukey
        Method to create an outliers object via the Tukey-based outlier
        detection. The 'distance' parameter refers to the number of
        interquartile range below the first and above the third 
        quartiles. 

        Parameters
        ----------
        distance : int, optional
            The multiplier for the IQR to determine the 
            outlier thresholds.
            Default equals 1.5.


        Return
        -------
        MethodTukey: An instance of the MethodTukey class 
        containing the results of the outlier detection.
        """
        return MethodTukey(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_Sn(self, distance=3):
        """ ## Sn method
        Method to create an outliers object via the Sn outlier
        detection.
        The idea of this method is :

        * For each participant, calculate the median distance to
        each other point.
        * After that, calculate the median of all this median distance.

        Distance refers to the multiplier of the median distance of 

        Parameters
        ----------
        distance : int, optional
            The multiplier for the Sn to determine the
            outlier thresholds.
            Default equals 3.

        Return
        ------
        MethodSn: An instance of the MethodSn class 
        containing the results of the outlier detection.
        """
        return MethodSn(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_prctile(self, distance=0.95):
        """ ## Percentile method
        Method to create an outliers object via the percentile method
        outlier detection.
        TODO
        Distance refers to the multiplier of the median distance of 

        Parameters
        ----------
        distance : int, optional
            The multiplier for the Sn to determine the
            outlier thresholds.
            Default equals 3.

        Return
        ------
        MethodSn: An instance of the MethodSn class 
        containing the results of the outlier detection.
        """
        return MethodPrctile(
            self.df,
            self.columns_to_test,
            self.participant_column,
            distance
        )

    @utils.check_number_entry
    def method_cutoff(
        self, 
        threshold, 
        filter = 'low-pass',
        threshold_included = True
        ):
        return MethodCutOff(
            self.df,
            self.columns_to_test,
            self.participant_column,
            threshold,
            filter,
            threshold_included
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

    def _calculate(
            self, 
            method
            ) -> None :
        """
        Private method used to calculate outliers.
        It iterates through the columns,
        calculates threshold values using the chosen method, 
        identifies outliers, and stores relevant information 
        such as the list of outliers, threshold values, and 
        their positions in the dataframe for each column
        The results are stored in instance attributes
        for further use in outlier management.

        This method is started at each instantation of a
        children of _Outliers.
        
        Parent _calculate is not used for rSD, Sn, Cut-off
        and identical. 

        Parameters
        ----------
        method : str
            Method for calculating outliers (iqr, sd)

        Returns
        -------
        None
        """
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
        return(0)

    def __str__(self) -> str:
        """
        Overloading of the __str__ method to modify the output
        of the print function.
        
        Format
        ------

        Title

        Headers :
        * Method used
        * Distance used
        * Column tested
        * Total number of outliers : number of participants that have
        at least one aberrant values
        * Total number of flagged values : number of values that are
        aberrant.

        Content :
        The column 1 has x outlier.
        Low threshold / High threshold
        
        ...

        """
        output_text = utils._title()

        if self.multi == True:
            output_text += utils._header_add_true(self)
            output_text += utils._content_add_true(self)

        else:
            output_text += utils._header_add_false(self)
            output_text += utils._content_add_false(self)
        return output_text[0:-2]

    def add(
            self, 
            to_add : str | list[str]
            ) -> None:
        """
        ## Add participant to the outlier object.

        This method allows adding specific index to the outlier object.
        The index corresponds to the name of the participant(s) in the
        referred participant column 
        (or initial index if not specified).

        It accepts either a single index or a list of index.
        Outliers added have a specific column in the summary.
        Thus, it is not possible to add outlier to a specific column.
        The function is returning None, so you just have to apply the 
        method without assigning it to another object.  
        Right way : obj.add("participant1")
        Wrong way : obj = obj.add("participant1")

        Parameters
        ----------
        to_add : str or list of str
            If you want to add only one index, you can input specify
            the index with a string.  
            If you want to add more than one index you want to add 
            with a single string or with a list of string.

        Raises
        ------
        KeyError
            If an attempt is made to add an object of type 
            '_Outliers' using this method.

        Returns
        -------
        None
            The method modifies the object in place and updates relevant parameters.

        Notes
        -----
        - If a string is provided, it is converted to a list with a single element.
        - If the 'added_manually' column already exists, the method extends it with unique elements 
        from the provided list, avoiding redundancy.
        - If the 'added_manually' column does not exist, it is created with the provided elements.
        - Other relevant parameters such as the count and position are updated accordingly.

        Example usage
        -------------
        ```python
        >>> out_obj.add("participant1")
        >>> out_obj.add(["participant1", "participant2"])
        ```

        Notes
        -----
        You can't add an outlier object with this method. 
        Use `ot.concat(out1, out2)` to concatenate outlier objects.
        """
        # If User input : out_obj.add("participant1")
        if isinstance(to_add, (str)):
            to_add = [to_add]
        
        # User input out_obj.add(["participant1", "participant2"]) or
        # string transform to list
        if isinstance(to_add, (list)):
            # if there is already a column added_manually coming from
            # a past addition, it extends it. If not, it create a new
            # key that have the value []. 
            # The comprehension list is to avoid redundancy
            self.dict_col.setdefault("added_manually", []).extend(
                list(set([elem for elem in to_add 
                 if elem not in self.dict_col["added_manually"]])))
            
            # Update other parameters
            self.nb["added_manually"] = len(self.dict_col["added_manually"])
            self.position["added_manually"] = utils._get_position(
                self.df, self.dict_col)
            self.all_index = utils._select_index(
                self.dict_col.keys(), self.dict_col)
        
        elif issubclass(type(to_add), _Outliers):
            raise KeyError('You can\'t add an outlier object'
                            ' with this method. \n'
                            'You can use ot.concat(out1, out2)')

        return None

    def remove(
            self, 
            to_remove : str | list[str] | dict[str: str|list[str]]
            ) -> None:
        """
        ## Remove outliers from the object.

        This method allows removing outliers from the object. For 
        example, if you detect outliers through a specific method, 
        you can judge that this participant is not really an outlier
        and remove him from the group of outliers. The function is 
        returning None, so you just have to apply the method without 
        assigning it to another object.   
        Right way : obj.remove("participant1")
        Wrong way : obj = obj.remove("participant1")

        Parameters
        ----------
        to_remove : str, list of str, or dict of str
            Outliers to subtract are input via the keyword `to_remove`.
            * If you want to delete one index from all columns, 
            you can simply input a string 
            (e.g., `obj.remove("participant1")`).
            * If you want to delete multiple indices from all columns,
            you can input a list of strings
            (e.g., `obj.remove(["participant1", "participant2"])`).
            * If you want to delete one or more indices from a 
            specific column, you can input a dictionary
            (e.g., `obj.remove({"Col1": "participant1"})`) or 
            `{"Col1": ["P1", "P2"]}`.

        Raises
        ------
        KeyError
            If the specified column is not present in the columns to 
            test in the dataframe.
        TypeError
            If the type of the input value is not supported.

        Returns
        -------
        None

        Example usage:
        ```python
        obj.remove("participant1")
        obj.remove(["participant1", "participant2"])
        obj.remove({"first_column": ["participant1", "participant2"]})
        ```

        Note: The method modifies the object in place and updates relevant parameters.
        """ 
        try:
            # User inputed 
            # Out_obj.sub(["participant1", "participant2"])
            if isinstance(to_remove, list):
                for column in self.dict_col:
                    o_str = [str(value) for value in to_remove]
                    self.dict_col[column] = [value for value in 
                                             self.dict_col[column]
                                             if str(value) not in o_str]
            # User inputed something like
            # Out_obj.sub({"first_column": ["participant1", "participant2"]})
            elif isinstance(to_remove, dict):
                for column in to_remove:
                    # transform to a list for allow iteration if user input :
                    # Out_obj.sub({"first_column": "participant1"})
                    if isinstance(to_remove[column], (int, str)):
                        to_remove[column] = [to_remove[column]]

                    to_remove[column] = [str(value) for value in to_remove[column]]

                    self.dict_col[column] = [value for value in 
                                             self.dict_col[column]
                                             if str(value) not 
                                             in to_remove[column]]

            # If there is just one participant index 
            # User inputed : Out_obj.sub("participant1")
            elif isinstance(to_remove, (int, str)):
                for column in self.dict_col:
                    self.dict_col[column] = [value for value 
                                             in self.dict_col[column]
                                            if str(value) != str(to_remove)]

        except KeyError as key:
            raise KeyError(f'It seems that the column "{column}"'
                           ' is not present in the columns'
                           ' to test in the dataframe') from key
        except TypeError as type:
            raise TypeError("This type of value is not "
                            "supported.") from type

        # Update parameters needed
        for column in self.columns_to_test:
            self.nb[column] = len(self.dict_col[column])
            self.position[column] = utils._get_position(
                self.df, self.dict_col)
        self.all_index = utils._select_index(
            self.dict_col.keys(), self.dict_col)

        return None
    
    def manage(
            self, 
            method: str = "delete" ,
            column: str | int | list[str] | list[int] = 'all'
            ) -> pd.DataFrame:
        """
        Manage outliers in the dataframe using specified method.

        After detecting outliers, this method allows you to manage them
        using different methods. You can choose to apply this method 
        only on specific columns.

        Parameters
        ----------
        method : {"delete", "na", "winsorise"}, optional   
            Method to manage outliers. Default is "delete".
            - 'delete': Delete the row if it contains 1 or more
            abberant values. Also known as truncation.
            - 'na': Replace all outliers with missing value NaN.
            - 'winsorise': Replace outliers with threshold values
            obtained through the outlier method used.

        column : str or int or list, optional
            Reference specific columns if you want to apply the manage
            method only on them. Default value take into account
            all columns.

        Returns
        -------
        pd.DataFrame
            A new dataframe with outliers managed based on the specified 
            method.

        Raises
        ------
        ValueError
            Winsorisation is not possible with "Sn" and "Identical" methods.
        """
        # ignore the format input for the column
        column = utils._process_column_to_test(self.df, column)
        
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
            aberrant_format: str = "value",
            other_value: str = "bool",
            all_participants: bool = False,
            all_columns: bool = False,
    ):
        """ ## Inspect in more details your outlier
        Inspect the dataframe for outliers and generate a 
        detailed table about them.

        Parameters
        ----------
        aberrant : {'value', 'bool'}, optional   
            Format for representing aberrant values.
            - 'value' (default): If an outlier value is detected, 
            the cell will contain the value of the outlier.
            - 'bool': If an outlier value is detected, the cell 
            will contain the boolean True.   

        other_value : {'bool', 'value'}, optional   
            Format for representing non-aberrant values.
            - 'bool' (default): If the value is not aberrant, the cell will 
            contain the boolean False.
            - 'value': If the value is not aberrant, the cell will contain 
            the actual value.

        all_participants : bool, optional   
            Include all participants or not.
            - False (default): Participants without aberrant values are not 
            present in the table.
            - True: Participants without aberrant values are included in the table.

        all_columns : bool, optional   
            Include all columns or not.
            - False (default): The table only contains columns that have been 
            chosen for testing. If the initial dataframe has 20 columns and 
            you choose to test 5 of them, the final table will contain 5 columns.
            - True: The table contains every column in the initial dataframe. 
            If the initial dataframe has 20 columns and you tested only 5 of 
            them, the final table will contain all 20 columns.

        Returns
        -------
        pd.DataFrame
            A table with detailed information about outliers based on the 
            specified parameters.
        
        Examples
        --------
        Imagine that 5 individuals (P8, P24, P32, P51) are considered 
        as outliers during the testing of 3 columns (Col2, Col5, Col8).
        P8 is an outlier in Col2, P24 in Col5, P32 in Col8, and P51 in
        Col2 and Col8. Each variable ranges from 0 to 20, and aberrant 
        values are those above 19 or below 1.
        
        ```python
        # Example 1 : If you just input default parameters   
        >>> result1 = your_instance.inspect()

        ```markdown
        |          | Col2 | Col5 | Col8 |
        |----------|------|------|------|
        | P8       |  20  | False| False|
        | P24      | False|  0.5 | False|
        | P32      | False| False| 19.5 |
        | P51      |  20  | False|  20  |
        ```python
        # Example 2 : Get the boolean matrix   
        >>> result2 = your_instance.inspect(aberrant = 'bool')
        ```markdown
        |          | Col2 | Col5 | Col8 |
        |----------|------|------|------|
        | P8       | True | False| False|
        | P24      | False| True | False|
        | P32      | False| False| True |
        | P51      | True | False| True |
        ```python
        # Example 3: Values that are not aberrant are shown
        >>> result3 = your_instance.inspect(other_value="value")
        ```markdown
        |          | Col2 | Col5 | Col8 |
        |----------|------|------|------|
        | P8       |  20  |  10  |  12  |
        | P24      |  12  |  0.5 |   4  |
        | P32      |  7   |  14  | 19.5 |
        | P51      |  20  |  8   |  20  |
        ```python
        # Example 4: Include all participants 
        >>> result4 = your_instance.inspect(other_value = "value",
                                            all_participants=True)
        ```markdown
        |          | Col2 | Col5 | Col8 |
        |----------|------|------|------|
        | P1       |  11  |  10  |  12  |
        | P2       |  13  |  0.5 |   4  |
        | P3       |  6   |  14  | 19.5 |
        | P4       |  4   |  8   |  20  |
        | P5       |  ..  |  ..  |  ..  |
        ```
        """
        table = pd.DataFrame(index=self.df.index)
        # the iteration on df.columns and not on keys of self.outliers
        # is present to conserve the order of columns in the initial
        # dataframe
        for column in self.df.columns:
            if column in self.dict_col:
                temporary_series = self.df[[column]].apply(
                    utils._parameters_of_the_table,
                    args=(aberrant_format, other_value, self.dict_col, column),
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
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.method = "Inter-quartile range"
        self.shortname = "iqr"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)


class MethodSd(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.method = "Standard Deviation"
        self.shortname = "sd"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)


class MethodRSd(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float,
        max_iteration: int,
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.max_iteration = max_iteration
        self.method = "Recursive Standard Deviation"
        self.shortname = "rsd"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)

    def _calculate(self, method):
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
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float,
        b: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.b = b
        self.method = "Median Absolute Distance"
        self.shortname = "mad"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)


class MethodTukey(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.method = "Tukey"
        self.shortname = "tukey"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)


class MethodSn(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        distance: int | float
    ) -> None:

        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = distance
        self.method = "Sn"
        self.shortname = "sn"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)

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
        self.shortname = "prctile"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate(self.shortname)


class MethodCutOff(_Outliers):
    def __init__(
        self,
        df: pd.DataFrame,
        columns_to_test: str | list | int | pd.Series,
        participant_column: str | int | pd.Series,
        threshold: int | float,
        filter: str,
        threshold_included: bool
    ) -> None:
        """
        Parameters
        ----------
        Comparison : {'low-pass', 'high-pass'}
        """
        self.df = df
        self.columns_to_test = columns_to_test
        self.participant_column = participant_column
        self.distance = threshold
        self.threshold = {}
        self.filter = filter
        self.threshold_included = threshold_included
        self.method = "Cut-Off"
        self.shortname = "cut-off"
        self.all_index = {}
        self.dict_col = {}
        self.threshold = {}
        self.nb = {}
        self.position = {}
        self.multi = False
        self._calculate()

    def _calculate(self):
        """ Private method used to calculate outliers """
        # get the function for calculate threshold
        for column in self.columns_to_test:
            # list of outliers by column
            if self.filter == "high-pass":
                list_outliers = self.df.index[
                    self.df[column] < self.distance
                ].tolist()
            else:
                list_outliers = self.df.index[
                    self.df[column] > self.distance
                ].tolist()
            # update parameters       
            self.dict_col[column] = list_outliers
            self.nb[column] = len(list_outliers)
            self.threshold[column] = self.distance
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
        # Redundant but it is used for print output
        self.distance = frequency
        self.threshold = {"Identical": frequency}
        self.multi = False
        self.method = "Identical"
        self.shortname = "id"
        self.all_index = {}
        self.dict_col = {}
        self.nb = {}
        self.position = {}
        self._calculate("identical")

    def _calculate(self, method):
        """ Private method used to calculate outliers """
        self.all_index = {}
        self.dict_col = {}
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
        self.dict_col["Identical"] = list_outliers
        self.nb["Identical"] = len(list_outliers)
        self.all_index = list_outliers
        self.position = utils._get_position(
            self.df, self.dict_col, self.shortname)

    def __str__(self):
        # I used this for avoid overiding columns to test at this 
        # moment. It overrides only when this identical method
        # is added to another object
        output_text = utils._title()
        output_text += utils._header_add_false(self)
        output_text += f"There are {self.nb['Identical']} " \
                       f"participant"\
                       f"{'s' if self.nb['Identical'] > 1 else ''}" \
                       f" with a frequency above {self.frequency} : "

        output_text += utils._outliers_index_presentation(self, "Identical")
        return output_text


class MethodMulti(_Outliers):
    def __init__(self, df):
        self.df = df
        self.method = []
        self.distance = {}
        self.nb = {}
        self.threshold = {}
        self.columns_to_test = []
        self.columns_to_test_w_method = {}
        self.position = {}
        self.multi = True
        self.shortname = []
        

