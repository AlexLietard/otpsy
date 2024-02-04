# Outliers Toolkit for Psychology, OTPsy

## Resume

Otpsy is a toolkit for detecting and managing outliers in your dataset with ease. Outliers, those data points that deviate significantly from the majority, can have a substantial impact on statistical analyses. My package gather various outlier detection methods, making it convenient for psychologists and data analysts to identify and handle outliers in a straightforward manner.
[Click here](/docs/glossary.md) for a glossary and [here](/docs/design.md) for a detailed explanation of the structure.

## Key Features

### 1. Multiple Methods for Outlier Detection

The package provides a range of outlier detection methods, allowing users to choose the most suitable approach for their specific needs. The available methods include:

* IQR (Interquartile Range)
* Tukey
* Standard Deviation (SD)
* Recursive Standard Deviation (rSD)
* Median Absolute Distance (MAD)
* $S_n$ Method
* Percentile
* Cut-off (e.g., response time under 80 ms)
* Identical response (for Likert scales or behavioral performance)
  
### 2. Visualisation

The Otpsy package enables users to effortlessly visualize outliers across multiple columns and methods simultaneously. This feature facilitates a comprehensive understanding of data distribution and threshold through histograms or scatter plots. The visualisation is running on plotly.

### 3. Easy Computation for Multiple Columns Testing

One of the major features of this package is its ability to efficiently compute outlier detection for multiple columns simultaneously. This streamlines the process for psychologists dealing with extensive datasets and diverse variables.

### 4. Simple Implementation

To get started, create a `sample` object by specifying the DataFrame, the columns to test, and the participant reference column. After the visualisation of the distribution, you can apply the desired outlier detection method using a method call, such as `sample.methodIQR()`. This will generate an outliers object containing the identified outliers.

### 5. Inspection and Management

After detection, the package allows for comprehensive inspection of the outliers using `print(outliers)`. It shows a string containing detailed information as we can usually see in R summary. Furthermore, with `outliers.inspect()` method, you obtains a DataFrame to inspect the value of outliers.  
It is possible to concat outliers object `.concat()`, add manually specific index `outliers.add()` or to substract an index `outliers.sub()`. They can be managed using the `outliers.manage()` method, providing options to remove, winsorize, or replace them with NaN values.

---

## Install and use otpsy

Otpsy is a python package. However, due to dependency issues, you still have to clone the package/

For now, the package only support pandas Dataframe and numpy array.
Imagine that you want to delete participants that have at least one
aberrant values on the Column 1, the Column 2 or the column 3.

```python
import otpsy as ot
import pandas as pd

# Import dataframe
df = pd.read_csv("example.csv")

# Select what has to be tested
sample = ot.Sample(dataframe, ["Col1", "Col2", "Col3"], "participant_name")

# Apply a specific method (mad) and remove outliers 
clean_df = sample.methodMAD(distance = 2.5).manage("delete")
```

For a more exhaustive presentation of functionnality, check the example folder.

---

## TODO

About outliers methods :

* Add self.position to multi and update parameters
* Check print output for each method

About visualisation :

* Hover text on shape or annotation or legend to understand which color corresponds to which method.
* Add summary to the left.
* Add the possibility to add user-input value (and thus percentile method)

About the structure :

* Create automated test
* Create tutorial
* Create data simulation
* Create a clear documentation (in progress)
* Create an export function to keep the information
