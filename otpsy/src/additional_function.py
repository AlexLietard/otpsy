import otpsy.src.main as main

def concat(obj1, obj2):  
    new_obj = main.MethodMulti()

    if issubclass(type(obj1), main._Outliers) and issubclass(type(obj2), main._Outliers):

        # Make all the parameter in the good format
        if obj1.multi == False: 
           obj_cleaned1 = change_format_of_attribute(obj1)
        if obj2.multi == False:
           obj_cleaned2 = change_format_of_attribute(obj1)

        # Concat the two elements here
        
        # Update of the method
        new_obj.method = obj_cleaned1.method + obj_cleaned2.method

        ## Update of the distance
        new_obj.distance = obj_cleaned1.distance
        
        # obj.distance = {Distance: shortname}
        for key2, value2 in obj_cleaned2.items():
            # avoid duplicate
            if value2 not in new_obj.distance[key2]:
                new_obj.distance.setdefault(key2, []).extend(value2)


        # Update threshold and the column associated with the method
        new_obj.columns_to_test_w_method = obj_cleaned1.columns_to_test_w_method
        new_obj.threshold = obj_cleaned1.threshold

        # columns_to_test_w_method = {Column: method}
        # threshold = {Column: {shortname: threshold}}
        for column in obj2.columns_to_test:
            # add method to each
            new_obj.columns_to_test_w_method.setdefault(column, []).\
                extend(obj2.method)
            
            # It is not possible to add two object of the same method
            # Anyway, it makes no sense.
            threshold_merge = obj_cleaned1.threshold[column] | \
                obj_cleaned2.threshold[column]
            new_obj.threshold.setdefault(column, {}).update(threshold_merge)

        # Add column to test associated with columns to test
        new_obj.columns_to_test = list(
            set(obj_cleaned1.columns_to_test 
                + obj_cleaned2.columns_to_test
        ))

        # Add number of outliers associated to a specific column and
        # avoid duplicate in outliers
        for column in new_obj.columns_to_test:
            new_obj.dict_col.setdefault(column, []).append(
                obj_cleaned2.dict_col)
            new_obj.dict_col[column] = list(set(
                new_obj.dict_col[column]
            ))
            new_obj.nb[column] = len(new_obj.dict_col[column])
    else:
        raise ValueError("Objects other than outliers are not supported.")
    return main.MethodMulti()

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
        obj.columns_to_test_w_method[column] = [
            str(obj.shortname[0])]
        # For each column, associate a method 
        # can be a error there due to percentile method
        obj.shortname_w_threshold[column] = {
            obj.shortname[0]: obj.threshold[column]}
        
    # really not the best way to do that but I'm currently struggling
    obj.threshold = obj.shortname_w_threshold
    return obj
        