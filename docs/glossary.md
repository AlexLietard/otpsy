# Glossary for the package

* Aberrant/Flagged Values: These are values that fall either above or below the threshold determined by the chosen method.

* Distance: This refers to user-inputted information, generally representing the multiplier of the parameters corresponding to the method (e.g., standard deviation for SD method, interquartile range for Tukey method). It is used to calculate the threshold.

* Outlier: A participant is considered an outlier if they have at least one aberrant value.

* Outliers Method: This is a specific method used to detect outliers (e.g., SD, MAD). It should not be confused with the computer term "method" which refers to the function applicable to an object.

* Outliers Object: A computer object containing all information about outliers detected through a specific method.

* Sample: It represents a subset of your data that you wish to test. This sample will undergo processing with the method of your choice.

* Threshold: The value obtained by multiplying the parameters (standard deviation, interquartile range) with the inputted distance. Thresholds can be categorized into two types: a low threshold, flagging all values below this value, and a high threshold, flagging all values above.
