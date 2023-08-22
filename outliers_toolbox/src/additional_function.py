def show_attributes() -> str:
    """ Show main attributes accessible

    The package compute automatically specific information about
    outliers or aberrant value. This function aim to show them.
    """
    final_text = "In this exhaustive summary, you will have to " \
                 "replace 'obj' by the name of your object.\n\n"
    final_text += "obj.outliers : dictionnary\n" \
                  "\tkey : column with at least one aberrant value / "\
                  "value : [index] " \
                  "of outliers\n"
    final_text += "obj.outliers_nb : dictionnary\n" \
                  "\tkey : column with at least one aberrant value / "\
                  "value: number of outliers for each column\n"
    final_text += "obj.threshold : dictionnary\n " \
                  "\tkey : column with at least one aberrant value / "\
                  "value : [low_threshold, high_threshold]\n" 
    final_text += "obj.outliers_index : list\n" \
                  "\tList containing all index with at least " \
                  "one aberrant value\n"
    
    return final_text


