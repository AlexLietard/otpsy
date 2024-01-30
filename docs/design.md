# Design

The package is organise around two main classes : the sample and the _Outliers. Both are dependent.

## Sample

### Instantiation

Firstly, the user needs to input a sample of their data into the Sample class. This action results in the creation of an instance of the class, accompanied by a few modifications to the entered data:

* Any user input in the columns_to_test (whether a string, the position of the column as an integer, or a list of columns) leads to the transformation of the columns into a list with their names as references, such as ["name_of_the_column1", "name_of_the_column2", ...].
* All columns undergo conversion to numeric values. In case of missing values, an object accessible through sample.missing is created. If only missing values are present, an error message is raised, specifying the column that triggered the error.
* The Participant column is designated as the index. If no column is specified, the default index is retained.

### Visualisation

Once this sample is defined, you can visualize data using a locally running dashboard on Dash with Plotly graphs. The visualization allow to visualise threshold for IQR, MAD, SD, rSD, Tukey, percentile, and cut-off method. However, it is not available for Sn and identical because they lack the same logic of a lower threshold and upper threshold. The visualization is straightforward, presenting either a scatter plot or histogram, with lines representing the threshold(s) and a specific color for each utilized method.

If the user opts not to visualize the data, they can directly apply a method to this sample. Each method of the Sample class (in a computational context) starting with .method_ corresponds to a statistical method for detecting outliers.

## Outliers object

In the realm of computing, the user is required to apply a specific method to define an instance corresponding to that method. For instance, if the user opts for the SD method, they can apply method_SD() to their Sample instance (`SampleInstance.method_SD()`) and obtain an instance of *MethodSD*. *MethodSD* is a subclass of the parent class *_Outliers*. In the typical scenario, it inherits the following methods from *_Outliers*:

* _calculate: private method to flagged aberrant values during instantiation
* \_\_str\_\_: Modify the magic method \_\_str\_\_ to alter the output of print. It provides a summary of attributes.
* add: add one or more index to the outliers object.
* remove: remove one or more index to the outliers object.
* manage: Determine how to handle outliers: **delete** them, apply **winsorization**, or replace them with **missing values**.
* inspect: inspect aberrant values and outliers with the creation of a dataframe showing aberrant values.

\_calculate is overridden for four methods: rSD, Sn, cut-off, identical. \_\_str\_\_ is overridden for the identical method. Each child object of the outliers class has multiple attributes accessible to the user. Let's take an instance of a child class named 'outliers'. Attributes can be categorized as user-dependent:

* outliers.df : df inputted by participant
* outliers.columns_to_test : List of names referring to columns to be tested.
* outliers.participant_column : column referring to the index of participants
* outliers.distance : inputted distance
* outliers.method : Method employed to detect outliers.
* outliers.shortname : Short name of the method used. This parameter is employed to retrieve the function `threshold_[shortname]` associated with the method in the config.py module.

Using this information, outliers will be computed, and data-dependent attributes will be obtained :

* outliers.dict_col : dictionnary having for each column a list of outliers index `{"Col1": ["index4", "index20"], "Col2": []}`.
* outliers.position : dictionnary having for each column a list of outliers row `{"Co1": [1, 4O], "Col2": []}`
* outliers.all_index : list of all index present in the outliers object
* outliers.threshold : dictionnary having for each column a tuple for the low and the high threshold (general case) `{"Col1" : (130, 200), "Col2": (20, 40)}`
* outliers.nb : dictionnary having for each column the number of aberrant values `{"Col1": 2, "Col2":0}`.
