from pandas.api.types import is_numeric_dtype, is_float_dtype
from inspect import signature
import pandas as pd
import numpy as np


class NewMissingValue:
    def __init__(self) -> None:
        self.nb = {}
        self.position = {}
        self.columns_converted = []
        self.new_missing_columns = []

    def __str__(self):
        final_text = f"""\
-----------------------------
Summary of new missing value
-----------------------------

{f'{", ".join(self.columns_converted)} has been converted to numeric.' 
    if len(self.columns_converted) > 0 
    else 'No column has been converted. Thus there is no missing value.'}
"""
        if len(self.new_missing_columns) > 0:
            final_text += f"""\
{", ".join(self.new_missing_columns)} present\
{'s' if len(self.new_missing_columns)==1 else ''} \
new missing value(s).\n"""

            final_text += "-"*30 + "\n"
            for column in self.new_missing_columns:
                final_text += f"The column {column} went from " \
                              f"{self.nb[column][0]} to {self.nb[column][1]}" \
                              f" (delta : {self.nb[column][2]}) missing value(s) : "

                if self.nb[column][2] > 0 and self.nb[column][2] <= 5:
                    text_position = [str(pos) for pos in self.position[column]]
                    final_text += ", ".join(text_position)

                elif self.nb[column][2] > 5:
                    final_text += str(self.position[column][0]) + ", " + \
                        str(self.position[column][1]) \
                        + "."*5 + ", " + \
                        str(self.position[column][-1])
                final_text += "\n"
            final_text += "print(object_name.missing.position) for all position"
        else:
            final_text += "There is no new missing values."
        return final_text


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

    before_transforming = df_func.isna().sum().sum()
    missing = NewMissingValue()

    # convert each column that is not a float
    # or integer
    for column in column_to_test_func:
        if not is_float_dtype(df_func[column]) or \
           not is_numeric_dtype(df_func[column]):
            # track the change on Na
            number_before = df_func[column].isna().sum()
            position_before = np.where(df_func[column].isnull())[0]

            # convert
            df_func[column] = pd.to_numeric(
                df_func[column].astype(str).
                str.replace(",", "."), errors='coerce')

            # prevent from an entire column with missing value
            if pd.isna(df_func[column]).all():
                raise TypeError(f"Can't convert {column} to numeric.")

            position_after = np.where(df_func[column].isnull())[0]
            missing.position[column] = list(
                set(position_after) - set(position_before))
            number_after = df_func[column].isna().sum()
            missing.nb[column] = (
                number_before, number_after, number_after-number_before)
            missing.columns_converted.append(column)

            if number_after > number_before:
                missing.new_missing_columns.append(column)

    after_transforming = df_func.isna().sum().sum()

    if len(missing.columns_converted) > 0 and \
            before_transforming < after_transforming:

        print(f"UserWarning: Column{'s' if len(missing.columns_converted)>0 else ''} : "
              f"{' & '.join(missing.columns_converted)} has "
              "been modified because they were "
              "not numeric. The number of missing "
              f"value went from {before_transforming} "
              f"to {after_transforming}. print(name_of_your_obj.missing) for "
              "more details.")
    return missing


def check_sample(function):
    """ Decorator to transform argument in the good format

    For parameters pass in the class Sample, there is
    a checking of the arguments passed.
    """
    def verify_arguments(*args, **kwargs):
        new_kwargs = {}

        # to associate the argument from args to the
        # keyword to have only kwargs
        kwargs = signature(function).bind(*args, **kwargs).arguments
        kwargs["column_to_test"] = kwargs.get("column_to_test", "")

        for key, value in kwargs.items():
            # check dataframe enter
            if key == "df":
                if not isinstance(value, (
                        pd.DataFrame, pd.Series, np.ndarray)):
                    raise TypeError("The argument entered for df "
                                    "is not supported.")

                if isinstance(value, np.ndarray):
                    value = pd.DataFrame(value, columns=["Tested"])

                elif isinstance(value, pd.Series):
                    value = value.to_frame()

                new_kwargs["df"] = value
                df = value

            # check column to test
            elif key == "column_to_test":
                pre_column = value
                if value == "all" or value == "":
                    try:
                        column_to_test = list(df.columns)
                    except AttributeError:
                        # in case its an pd.Series
                        if isinstance(df, pd.Series):
                            column_to_test = [df.name]
                        else:
                            raise ValueError("Can't extract "
                                             "the column to test")

                    # To avoid the conversion of the participant
                    # column where this is not the purpose
                    try:
                        column_to_test.remove(kwargs["participant_column"])
                    except:
                        pass
                else:
                    column_to_test = _process_column_to_test(df, pre_column)
                missing = _convert_column_to_numeric(df, column_to_test)
                new_kwargs[key] = column_to_test
                new_kwargs["missing"] = missing

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


def _get_position(df, dict_col, dimin = ""):
    if dimin == "id":
        index_to_find = dict_col
    else:       
        index_to_find = _select_index(dict_col.keys(), dict_col)
    position_index = []
    for index in index_to_find:
        position_index.append(df.index.get_loc(index))
    position_index.sort()
    return position_index


def header_add_true(obj):
    output_text = ""
    # show method used
    output_text += f"Method used  : {', '.join(obj.method)}\n"

    # show distance used
    output_text += f"Distance used : "
    for distance in obj.distance:
        output_text += f"{distance} ({', '.join(obj.distance[distance])}), "
    output_text = output_text[0:-2] + "\n"

    # Show column tested
    output_text += "Column tested : "
    for column in obj.columns_to_test:
        output_text += f"{column} (" \
            f"{', '.join(obj.columns_to_test_w_method[column])}), "

    output_text = output_text[0:-2] + "\n"
    output_text += "-"*30 + "\n"
    return output_text


def header_add_false(obj):
    output_text = ""
    output_text += f"Method used : {obj.method}\n"
    output_text += f"Distance used : {obj.distance}\n"
    output_text += f"Column tested : {', '.join(obj.columns_to_test)}\n" \
        + "-"*30 + "\n"
    return output_text


def content_add_true(obj):
    output_text = ""
    for column in obj.columns_to_test:
        output_text += f"The column {column} has " \
            f"{obj.nb[column]} outliers : "

        if obj.nb[column] > 0 and obj.nb[column] <= 5:
            output_text += ", ".join([str(val)
                                      for val in obj.dict_col[column]])

        elif obj.nb[column] > 5:
            output_text += str(obj.dict_col[column][0]) + ", " + \
                str(obj.dict_col[column][1]) \
                + "."*5 + ", " + \
                str(obj.dict_col[column][-1])
        else:  # if there is no outliers
            output_text = output_text[0:-3] + "."  # take out last ":"

        output_text += "\n"

        for method in obj.threshold[column]:
            # This is because Sn and cut-off have only one threshold value
            if method == "sn" or method == "cut-off":
                output_text += f"{method.upper()}: " \
                    f"{round(obj.threshold[column][method], 2)} ; "
            else:
                output_text += f"{method.upper()}:" \
                    f" low: {round(obj.threshold[column][method][0], 2)} / "\
                    f"high: " \
                    f"{round(obj.threshold[column][method][1], 2)} ; "\

        output_text = output_text[0:-2] + "\n\n"
    return output_text


def content_add_false(obj):
    output_text = ""
    for column in obj.columns_to_test:
        output_text += f"The column {column} has " \
            f"{obj.nb[column]} outliers : "

        if obj.nb[column] > 0 and obj.nb[column] <= 5:
            output_text += ", ".join([str(val)
                                      for val in obj.dict_col[column]])

        elif obj.nb[column] > 5:
            output_text += str(obj.dict_col[column][0]) + ", " + \
                str(obj.dict_col[column][1]) \
                + "."*5 + ", " + \
                str(obj.dict_col[column][-1])
        else:  # if there is no outliers
            output_text = output_text[0:-3] + "."  # take out last ":"

        if obj.method == "Sn":
            output_text += "\nThreshold median distance to other " \
                f"point is {round(obj.threshold[column], 2)} \n\n"
        else:
            output_text += "\nLow threshold : " \
                f"{round(obj.threshold[column][0], 2)} / "\
                f"High threshold : {round(obj.threshold[column][1], 2)}"\
                "\n\n"
    return output_text
