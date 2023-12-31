# Outliers Toolkit for Psychology, OTPsy

## Resume

Outliers are data point that are extremely distant from most of other data points.In the last decades, lot of methods to detect outliers in a statistical distribution arised.  
This package has the purpose to sum up the different method and to be able to used the different method without difficulty in psychology. The **particularity** is that it allows easily the computation of multiple columns testing.

For now, the package allows to detect outliers with a user-inputed distance with the method :

* IQR (IQR distance to median)
* Tukey (IQR distance from quartiles)
* Standard Deviation SD
* Recursive Standard Deviation rSD
* Median Absolute Distance MAD
* $S_n$ method
* Percentile
* Cut-off (reponse time under 80 ms for example)
* Identical response (for likert scale for example or behavioral performance)

The detection is made through the creation of an `sample` object in which you specify the df, the columns to test and the column refering to the participant.

After the detection, they can be inspect through the inspect() method which returns a dataframe.
Outliers can be remove, winsorise or replace by na with the method `manage()`.

---

## Example

Imagine that you realise a study in which you want to explore the influence of art exposition on visual exploration of angry face. Thus, you collect data about the explored time of the painting scene, number of fixations of anger face (or another DV), score on depression and anxiety.
With this data, you want to control for different things :

* Does participants look at the scene ?

---

## TODO

About visualisation :

* Hover text on shape or annotation or legend to understand which color corresponds to which method.
* Add summary to the left
* Add all methods to the visualisation, with the possibility to add user-input value.

About outliers method :

About the structure :

* Create automated test
* Create tutorial
* Create data simulation
* Create a clear documentation (in progress)
* Create an export function to keep the information
