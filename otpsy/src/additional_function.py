import otpsy.src.main as main
import otpsy.src.utils as utils

from copy import deepcopy

def concat(
        to_concat: list, 
        df_to_keep: int = 0
    ) -> main.MethodMulti :
    """ # Concatenate outliers object together
    The concat function is designed to concatenate
    multiple outliers objects efficiently. It takes a list of 
    outliers objects (to_concat) and an optional parameter 
    (df_to_keep) representing the index of the dataframe 
    to retain during concatenation.   
    If the same column is present in two different outliers object,
    the outliers will be keep only for the last object added. 
    It doesn't make sense to detect outliers with 2 methods, so it is
    highly discourage.
    ---

    Parameters
    ----------
    to_concat : list of outliers object
        List of outlier objects to concatenate. The order of objects 
        in the list determines the concatenation sequence.

    df_to_keep : int, optional
        Index of the dataframe to retain during concatenation. 
        Default is 0.
        It means that the dataframe of the first object in the list 
        (`to_concat[0]`) is retained.

    Returns
    -------
    main.MethodMulti
        A new outlier object resulting from the concatenation of the
        input outlier objects.

    Raises
    ------
    ValueError
        The function expects all objects in the `to_concat` list to be
        child instance of the `main._Outliers` class. It means that
        the object has to be an outlier object.

    Example
    -------
    >>> import otpsy as ot
    >>> sample = otpsy.Sample(...)  # Replace ... with appropriate parameters
    >>> obj1 = sample.method_IQR(...)
    >>> obj2 = sample.identical(...) 
    >>> combined_object = pd.concat([obj1, obj2], 0)
    
    Notes
    -----
    The fundamental concept underlying this function is to commence
    the concatenation process by adding obj1 to obj2.
    If there are more than two objects to concatenate, the function
    iteratively incorporates the result obtained from the concatenation
    and adds the n-th object to this intermediate result. The reason for
    returning a Multi object is that it deviates from the format of
    simple main._Outliers subclasses.   
    This deviation is particularly notable in the implementation of
    the __str__ method.
    """
    for i in range(1, len(to_concat)):
        obj1 = to_concat[0] if i == 1 else new_obj
        obj2 = to_concat[i]

        new_obj = main.MethodMulti(to_concat[0].df)
        if issubclass(type(obj1), main._Outliers) and issubclass(type(obj2), main._Outliers):
            new_obj = _concat_both_object(new_obj, obj1, obj2)

        else:
            raise ValueError("Objects other than outliers are not supported.")
    return new_obj


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
    for column in obj2.columns_to_test:
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

    new_obj.all_index = utils._select_index(
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

    # distance
    obj.distance = {obj.distance: [obj.shortname]}

    # short name
    obj.shortname = [obj.shortname]

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
        