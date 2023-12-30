import otpsy.src.main as main
import otpsy.src.utils as utils

from copy import deepcopy

def concat(to_concat: list, df_to_keep: int = 0):

    for i in range(1, len(to_concat)):
        obj1 = to_concat[0] if i == 1 else new_obj
        obj2 = to_concat[i]

        new_obj = main.MethodMulti(to_concat[0].df)
        if issubclass(type(obj1), main._Outliers) and issubclass(type(obj2), main._Outliers):
            new_obj = update_the_attribute(new_obj, obj1, obj2)

        else:
            raise ValueError("Objects other than outliers are not supported.")
    return new_obj

def update_the_attribute(new_obj, obj1, obj2):
    
    # Make all the parameter in the good format
    if obj1.multi == False: 
        obj1_cleaned = change_format_of_attribute(deepcopy(obj1))
    else:
        obj1_cleaned = deepcopy(obj1)
    
    if obj2.multi == False:
        obj2_cleaned = change_format_of_attribute(deepcopy(obj2))
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

def change_format_of_attribute(obj):
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
        