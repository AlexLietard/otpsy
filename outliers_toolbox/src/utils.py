import pandas as pd
from pandas.api.types import is_numeric_dtype, is_float_dtype
from inspect import signature


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
        if pre_participant_column not in df_func.columns \
                and pre_participant_column != "":
            raise NameError("The column you enter is not in the dataframe")
        participant_column = pre_participant_column
    else:
        raise TypeError(f"The type of data {type(pre_participant_column)} "
                        "is not supported to refer column.")
    return participant_column


def _process_distance(value):
    try:
        distance = float(str(value).replace(r"\.", ","))
    except ValueError:
        raise ValueError("You need to enter a numeric "
                         "(a float or an integer) value.") \
            from ValueError
    return distance


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
        if not is_float_dtype(df_func[column]) or \
           not is_numeric_dtype(df_func[column]):
            df_func[column] = pd.to_numeric(
                df_func[column].astype(str).
                str.replace(",", "."), errors='coerce')
        columns_modified.append(column)

    after_transforming = df_func.isna().sum().sum()

    if len(columns_modified) > 0 and before_transforming < after_transforming:
        print(f"UserWarning: Columns {columns_modified} has "
              "been modified because they were "
              "not numeric. When it was not "
              "convertible to numeric, it gave new "
              "missing value. The number of missing "
              f"value went from {before_transforming} "
              f"to {after_transforming}.")


def check_Sample(function):
    """ Decorator to transform argument in the good format

    For parameters pass in the class Sample, there is
    a checking of the arguments passed.
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
                new_kwargs[key] = column_to_test

            # check participant column
            elif key == "participant_column":
                pre_participant_column = value
                participant_column = _process_participant_column(
                    df, pre_participant_column)

                # avoid potential overlap between column
                # to test and participant column
                try:
                    if participant_column in column_to_test:
                        raise ValueError("The participant column can't "
                                         "be in the columns you want to test")
                except UnboundLocalError:
                    pass
                new_kwargs["participant_column"] = participant_column

            # check distance
            elif key == "distance":
                new_kwargs["distance"] = _process_distance(value)

            elif key == "threshold":
                new_kwargs["threshold"] = _process_distance(value)

        # to pass self when its decorating class
        if "self" in kwargs:
            func = function(kwargs["self"], **new_kwargs)
        else:
            func = function(**new_kwargs)
        return func

    return verify_arguments


def check_number_entry(function):
    """ Check the argument pass for the detection of outliers """
    def verify_arguments(*args, **kwargs):
        new_kwargs = {}

        # to associate the argument from args to the
        # keyword to have only kwargs
        kwargs = signature(function).bind(*args, **kwargs).arguments

        for key, value in kwargs.items():
            # check dataframe enter
            if key == "distance":
                new_kwargs["distance"] = _process_distance(value)

            elif key == "threshold":
                new_kwargs["threshold"] = _process_distance(value)

            elif key == "iteration":
                new_kwargs["iteration"] = _process_distance(value)

            elif key == "frequency":
                frequency = _process_distance(value)
                if frequency > 1:
                    raise ValueError("Frequency must be inferior to 1")
                new_kwargs["frequency"] = frequency
            
            elif key == "b":
                new_kwargs["b"] = _process_distance(value)

        # to pass self when its decorating class
        if "self" in kwargs:
            func = function(kwargs["self"], **new_kwargs)
        else:
            func = function(**new_kwargs)
        return func
    return verify_arguments


def _select_index(column_to_keep, dict_col) -> list:
    """Private method to take all value of the dictionnary
    self.outliers and clean it
    """
    # remove list in the list
    # column to keep is for a specific function
    index_to_delete = [
        index for key, value in dict_col.items()
        for index in value if key in column_to_keep
    ]
    # avoid duplicate
    return list(set(index_to_delete))


def _parameters_of_the_table(x, aberrant, other_value, outliers, column):
    """Private method to manage the output of the table of obj.inspect()"""
    if x.name in outliers[column]:
        final = x[column] if aberrant == "value" else True
    else:
        final = False if other_value == "bool" else x[column]
    return final


def _get_position(df, dict_col):
    index_to_find = _select_index(dict_col.keys(), dict_col)
    position_index = []
    for index in index_to_find:
        position_index.append(df.index.get_loc(index))
    position_index.sort()
    return position_index
