# Design

The package is organise around two main classes : the sample and the _Outliers. Both are dependent.

## Sample

### Instantiation

First of all, user needs to enter a sample of its data to the Sample class. It creates an instance of the class with a few modification to the data :

* whatever the user enters on columns_to_test (a string, the position of the column (int), or a list of columns places), the columns are **implemented in a list of columns with their names** as a reference `["name_of_the_column1", "name_of_the_column2",...]`.
* Participant column is set to index. If there is no column specified, the default index is keep.
* All columns are converted to numeric. If some missing values occurs, an object accessible via `sample.missing` is allow. If there are only missing values, it raises an error message specifying the column creating the error.

### Visualisation

After this sample defined, it is possible to visualise it through a dashboard running locally on plotly and dash. The visualisation will be available in the first time for IQR, MAD, SD, rSD, Tukey, percentile, cut-off. It is not available for Sn and identical because they didn't have the same logic of a lower threshold and upper threshold. The visualisation is quite simple, can be either a scatter plot or histogram, with lines representing the threshold(s) with a specific color for each method used.
If the user don't want to visualise data, it is directly possible to apply a method on this sample. Each sample method (in a computer meaning) starting by `.method_` refers to a statiscal method to detect outliers.

## Outliers object

Computer-wise, apply a specific method define an instance corresponding to the method. For example, if the user choose SD method, then them apply `sample.method_SD()` and have an get an instance of `MethodSD`. Method_SD is a child class of the parent class \_Outliers. It inherit from parent.
