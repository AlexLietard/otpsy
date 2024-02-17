import src.otpsy.main as main
import src.otpsy.utils as utils

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
    The fundamental concept underlying this function is that concat
    starts the concatenation process by adding obj1 to obj2.
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
            new_obj = utils._concat_both_object(new_obj, obj1, obj2)

        else:
            raise ValueError("Objects other than outliers are not supported.")
    return new_obj

def help_print():
    txt = """\
PARAMETERS DECRIPTION
-------------------------

Method used : The method you used to detect outliers
Distance used : The distance you used to detect outliers
Column tested : The column on which outliers have been detected
Total number of outliers : The number of participants having at least
one aberrant values
Total number of flagged values : The number of aberrant values detected
    """
    return txt