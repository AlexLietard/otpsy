from pandas.api.types import is_numeric_dtype, is_float_dtype
from inspect import signature
import pandas as pd
import numpy as np
from copy import deepcopy


class NewMissingValue:
    def __init__(self) -> None:
        self.nb = {}
        self.position = {}
        self.columns_converted = []
        self.new_missing_columns = []

    def __str__(self):
        final_text = f"""\
----------------------------
Summary of new missing value
----------------------------

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
    columns_to_test = []

    # if the user enters the Series
    if isinstance(pre_column, pd.Series):
        columns_to_test.append(pre_column.name)

    # to select all columns
    elif pre_column == 'all':
        columns_to_test.extend(list(df_func.columns))

    # if the person enters the name of one column
    elif isinstance(pre_column, str):
        if pre_column not in df_func.columns:
            raise NameError("The column you enter is not in the dataframe.")
        columns_to_test.append(pre_column)

    # if the person enters the index of the column
    elif isinstance(pre_column, int):
        columns_to_test.append(df_func.iloc[:, pre_column].name)

    # if the person enters a list
    elif isinstance(pre_column, list):

        # There is three possibilities :
        # * either it contains the name of the columns,
        # * either it contains the pd.Series
        # * either it contains a list of index

        for col in pre_column:
            # If it's column
            if isinstance(col, pd.Series):
                columns_to_test.append(col.name)

            # If it's name, check its presence in the dataframe
            elif isinstance(col, str):
                if col not in df_func.columns:
                    raise NameError(f"The column \"{col}\" you enter "
                                    "is not in the dataframe")
                columns_to_test.append(col)

            # it is the index of column
            elif isinstance(pre_column, int):
                columns_to_test.append(df_func.iloc[:, col].name)
    else:
        raise TypeError(f"The type of data {type(pre_column)} "
                        "is not supported to refer column.")
    return columns_to_test


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
            raise NameError(f"The column you enter (\"{pre_participant_column}\")"
                            " is not in the dataframe")
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


def _check_sample(function):
    """ Decorator to transform argument in the good format

    For parameters pass in the class Sample, there is
    a checking of the arguments passed.
    """
    def verify_arguments(*args, **kwargs):
        new_kwargs = {}

        # to associate the argument from args to the
        # keyword to have only kwargs
        kwargs = signature(function).bind(*args, **kwargs).arguments
        kwargs["columns_to_test"] = kwargs.get("columns_to_test", "")

        for key, value in kwargs.items():
            # check dataframe enter
            if key == "df":
                if not isinstance(value, (
                        pd.DataFrame, pd.Series, np.ndarray, list)):
                    raise TypeError("The argument entered for df "
                                    "is not supported.")

                if isinstance(value, np.ndarray) or isinstance(value, list):
                    value = pd.DataFrame(value, columns=["Tested"])

                elif isinstance(value, pd.Series):
                    value = value.to_frame()

                new_kwargs["df"] = value
                df = value

            # check column to test
            elif key == "columns_to_test":
                pre_column = value
                if value == "all" or value == "":
                    try:
                        columns_to_test = list(df.columns)
                    except AttributeError:
                        # in case its an pd.Series
                        if isinstance(df, pd.Series):
                            columns_to_test = [df.name]
                        else:
                            raise ValueError("Can't extract "
                                             "the column to test")

                    # To avoid the conversion of the participant
                    # column where this is not the purpose
                    try:
                        columns_to_test.remove(kwargs["participant_column"])
                    except:
                        pass
                else:
                    columns_to_test = _process_column_to_test(df, pre_column)
                missing = _convert_column_to_numeric(df, columns_to_test)
                new_kwargs[key] = columns_to_test
                new_kwargs["missing"] = missing

            # check participant column
            elif key == "participant_column":
                pre_participant_column = value
                participant_column = _process_participant_column(
                    df, pre_participant_column)

                # avoid potential overlap between column
                # to test and participant column
                try:
                    if participant_column in columns_to_test:
                        raise ValueError("The participant column can't "
                                         "be in the columns you want to test")
                except UnboundLocalError:
                    pass
                new_kwargs["participant_column"] = participant_column



        # to pass self when its decorating class
        if "self" in kwargs:
            func = function(kwargs["self"], **new_kwargs)
        else:
            func = function(**new_kwargs)
        return func

    return verify_arguments


def _check_number_entry(function):
    """ Check the argument pass for the detection of outliers """
    def verify_arguments(*args, **kwargs):
        new_kwargs = {}

        # to associate the argument from args to the
        # keyword to have only kwargs
        kwargs = signature(function).bind(*args, **kwargs).arguments

        for key, value in kwargs.items():
            # check dataframe enter
            if key == "frequency":
                frequency = _process_distance(value)
                if frequency > 1:
                    raise ValueError("Frequency must be inferior to 1")
                new_kwargs["frequency"] = frequency

            # check distance and threshold
            elif key == "distance" or key == "threshold" \
                or key == "low_threshold" or key == "high_threshold":
                new_kwargs[key] = _process_distance(value)

            elif key == "threshold_included" or key == "filter" or key == "b"\
                or key == "iteration":
                new_kwargs[key] = value


        # to pass self when it's decorating class
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
    index_to_select = [
        index for key, value in dict_col.items()
        for index in value if key in column_to_keep
    ]
    # avoid duplicate
    index_to_select_clean = list(set(index_to_select))
    index_to_select_clean.sort()
    return index_to_select_clean


def _parameters_of_the_table(x, aberrant, other_value, outliers, column):
    """Private method to manage the output of the table of obj.inspect()"""
    if x.name in outliers[column]:
        final = x[column] if aberrant == "value" else True
    else:
        final = False if other_value == "bool" else x[column]
    return final


def _get_position(df, index_to_find, shortname = ""):
    position_index = []
    try:
        for index in index_to_find:
            position_index.append(df.index.get_loc(index))
    except KeyError as e:
        raise KeyError(f"The index \"{index}\" seems to not"
                       " be in the column refering to participant.")
    position_index.sort()
    return position_index


def _header_add_true(obj):
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
    output_text += f"Total number of outliers : {len(obj.all_index)}\n"
    output_text += f"Total number of flagged values : " \
        f"{sum(obj.nb.values())}\n"
    output_text += "-"*30 + "\n\n"
    return output_text


def _header_add_false(obj):
    output_text = f"""\
Method used : {obj.method}
Distance used : {obj.distance}
Column tested : {', '.join(obj.columns_to_test)}
Total number of outliers : {len(obj.all_index)}
Total number of flagged values : {sum(obj.nb.values())}
{'-'*30}

"""
    return output_text


def _content_add_true(obj):
    output_text = ""
    for column in obj.columns_to_test:
        if column == "Identical":
            output_text +=f"There are {obj.nb[column]} " \
                       f"participant"\
                       f"{'s' if obj.nb['Identical'] > 1 else ''} with " \
                       f"a frequency above {obj.threshold['Identical']['id']} : "
        else:
            output_text += f"The column {column} has " \
                f"{obj.nb[column]} outlier"\

        output_text += _s_if_needed(obj.nb[column])
        output_text += _outliers_index_presentation(obj, column)

        output_text += "\n"

        for shortname in obj.threshold[column]:
            # This is because Sn and cut-off have only one threshold value
            if shortname == "sn":
                output_text += f"{shortname.upper()}: " \
                    f"{round(obj.threshold[column][shortname], 2)} ; "
            # The user already know the threshold
            elif shortname == "id":
                pass
            else:
                output_text += f"{shortname.upper()}:" \
                    f" low: {round(obj.threshold[column][shortname][0], 2)} / "\
                    f"high: " \
                    f"{round(obj.threshold[column][shortname][1], 2)} ; "\

        output_text = output_text[0:-2] + "\n\n"
    return output_text


def _content_add_false(obj):
    output_text = ""
    for column in obj.columns_to_test:
        output_text += f"The column {column} has " \
            f"{obj.nb[column]} outlier"
        output_text += _s_if_needed(obj.nb[column])
        output_text += _outliers_index_presentation(obj, column)
        output_text += "\n"
        if obj.method == "Sn":
            output_text += "Threshold median distance to other " \
                f"point is {round(obj.threshold[column], 2)}\n\n"
        else:
            output_text += "Low threshold : " \
                f"{round(obj.threshold[column][0], 2)} / "\
                f"High threshold : {round(obj.threshold[column][1], 2)}"\
                "\n\n"

    if "added_manually" in obj.dict_col.keys():
        output_text += "You added manually "\
            f"{len(obj.dict_col['added_manually'])} "\
            f"outlier{'s : ' if obj.nb['added_manually'] != 0 else '.'}"
        output_text += _outliers_index_presentation(obj, "added_manually")
        output_text += "\n\n"
    return output_text


def _outliers_index_presentation(obj, column):
    """ ! Private method ! 
    Allow to present a sample of index for the print output.

    There are 3 cases:

    * If there are no outliers, output_text = ""
    * If there are less than or equal 5 outliers, output
    text is composed of the index of all outliers
    * If there are more than 5 outliers, the first two and
    the last index are shown to the user.
    """
    output_text = ""
    if obj.nb[column] > 0 and obj.nb[column] <= 5:
        output_text += ", ".join([str(val)
                                    for val in obj.dict_col[column]])

    elif obj.nb[column] > 5:
        output_text += str(obj.dict_col[column][0]) + ", " + \
            str(obj.dict_col[column][1]) \
            + "."*5 + ", " + \
            str(obj.dict_col[column][-1])

    return output_text


def _title():
    output_text = "-"*33
    output_text += "\nSummary of the outliers detection\n"
    output_text += "-"*33
    output_text += "\n\n"
    return output_text


def _s_if_needed(nb):
    if nb == 0:
        output_text = "."
    elif nb == 1:
        output_text =" : "
    else:
        output_text = "s : "
    return output_text


def _concat_both_object(new_obj, obj1, obj2):
    """
    # ! Private Function !
    Used to concat obj1 and obj2 to return a new obj. Basically,
    the concatenation corresponds to the update of the different
    attributes and put this attribute into a Method-Multi object.

    Parameters
    ----------
    new_obj : main.MethodMulti
        The statistical object to be updated.
        
    obj1 : child of main._Outliers
        The first outliers object to be concatenated.
        
    obj2 : child of main._Outliers
        The second outliers object to be concatenated.

    Returns
    -------
    main.MethodMulti
        The updated outliers object.

    Notes
    -----
    The function _update_the_attribute takes two outliers objects
    (obj1 and obj2) and a target object (new_obj) as input.
    It standardizes the format of the input objects, concatenates
    their information by updating the attributes of the target
    object accordingly. The updates include combining methods,
    distances, thresholds, columns to test with associated methods,
    and the number of outliers associated with specific columns.
    Finally, it returns the updated target object (new_obj).
    """
    
    # Make all the parameter in the good format
    if obj1.multi == False: 
        obj1_cleaned = _change_format_of_attribute(deepcopy(obj1))
    else:
        obj1_cleaned = deepcopy(obj1)
    
    if obj2.multi == False:
        obj2_cleaned = _change_format_of_attribute(deepcopy(obj2))
    else:
        obj2_cleaned = deepcopy(obj2)

    # Concat the two elements here
    
    ## Update of the method
    new_obj.method = obj1_cleaned.method + obj2_cleaned.method

    ## Update of the distance
    new_obj.distance = obj1_cleaned.distance
    
    ### obj.distance = {Distance: shortname}
    for key2, value2 in obj2_cleaned.distance.items():
        # avoid duplicate
        new_obj.distance.setdefault(key2, []).extend(value2)
        new_obj.distance[key2] = list(set(new_obj.distance[key2]))


    # Update threshold and the column associated with the method
    new_obj.columns_to_test_w_method = \
        obj1_cleaned.columns_to_test_w_method
    
    new_obj.threshold = obj1_cleaned.threshold
    # columns_to_test_w_method = {Column: method}
    # threshold = {Column: {shortname: threshold}}
    for column in obj2_cleaned.columns_to_test:
        # add method to each
        new_obj.columns_to_test_w_method.setdefault(column, []).\
            extend(obj2_cleaned.shortname)
        
        # It is not possible to add two object of the same method
        # Anyway, it makes no sense.
        threshold_merge = obj1_cleaned.threshold.get(column, {}) | \
            obj2_cleaned.threshold[column]
        new_obj.threshold.setdefault(column, {}).update(threshold_merge)

    # Add column to test associated with columns to test
    new_obj.columns_to_test = list(
        set(obj1_cleaned.columns_to_test 
            + obj2_cleaned.columns_to_test
    ))

    # Add number of outliers associated to a specific column and
    # avoid duplicate in outliers
    new_obj.dict_col = obj1_cleaned.dict_col
    for column in obj2_cleaned.columns_to_test:
        new_obj.dict_col.setdefault(column, []).extend(
            obj2_cleaned.dict_col[column])
        new_obj.dict_col[column] = list(set(
            new_obj.dict_col[column]
        ))
    for column in new_obj.columns_to_test:
        new_obj.nb[column] = len(new_obj.dict_col[column])
        new_obj.position[column] = _get_position(new_obj.df, 
                                                 new_obj.dict_col[column])

    new_obj.all_index = _select_index(
        new_obj.dict_col.keys(), new_obj.dict_col)
    
    return new_obj


def _change_format_of_attribute(obj):
    """ ! Private Method !
    Change the format of an outlier object's attributes for consistency.

    Parameters
    ----------
    obj : main._Outliers
        The outlier object to be formatted.

    Returns
    -------
    main._Outliers
        The formatted outlier object.
    """
    obj.columns_to_test_w_method = {}
    obj.shortname_w_threshold = {}
    # method
    obj.method = [obj.method]

    if obj.shortname == "cut-off":
        obj.distance = tuple(obj.distance)
    # distance
    obj.distance = {obj.distance: [obj.shortname]}

    # short name
    obj.shortname = [obj.shortname]
    if obj.shortname == ["id"]:
        obj.columns_to_test = ["Identical"]

    for column in obj.columns_to_test:
        # associate colum with method
        # possibility to increase te rapidity ?
        obj.columns_to_test_w_method[column] = [
            str(obj.shortname[0])]
        # For each column, associate a method 
        # can be a error there due to percentile method
        obj.shortname_w_threshold[column] = {
            obj.shortname[0]: obj.threshold[column]}
        
    # really not the best way to do that but I'm currently struggling
    obj.threshold = obj.shortname_w_threshold

    return obj
        