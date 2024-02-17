# Mathematical description

This document serves the purpose of mathematically detailing the computations performed by each method.

## Interquartile range (IQR)

The interquartile range method (IQR, `.method_IQR()`) determines the threshold by considering a specified number of interquartile ranges from the median. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = med - IQR \cdot \lambda \\
        t_h = med + IQR \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, $med$ corresponds to the median, $IQR$ corresponds to $Q3-Q1$, and $\lambda is the distance inputted by user (default: 2).
An aberrant value is identified when it falls below the low threshold or exceeds the high threshold.

---

## Tukey (tukey)

The Tukey method (tukey, `.method_tukey()`) computes threshold as a specified number of interquartile range from the first quartile or the third quartile. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = Q1 - IQR \cdot \lambda \\
        t_h = Q3 + IQR \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, $Q1$ the first quartile, $Q3$ the third quartile, $\lambda$ the distance inputted (default: 1.5). An aberrant value is identified when it falls below the low threshold or exceeds the high threshold.

---

## Standard deviation (SD)

The Standard deviation method (SD, `.method_SD()`) computes the threshold as a specified number of standard deviation from the mean. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = \overline{x} - SD \cdot \lambda \\
        t_h = \overline{x} + SD \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold,$\overline{x}$ the mean, $SD$ the standard deviation, $\lambda$ the distance inputted (default: 2.5). An aberrant value is identified when it falls below the low threshold or exceeds the high threshold.

---

## Recursive standard deviation (rSD)

The recursive standard deviation method (rSD, `.method_rSD()`) computes the threshold as the specified number of standard deviation (default: 3) from the mean, and continue to compute the threshold until there is no outlier or the maximal iteration is reached (default: 3). Formally,
$$
\left\{
    \begin{array}{ll}
        t_l^0 = \overline{x} - SD \cdot \lambda \\
        t_h^0 = \overline{x} + SD \cdot \lambda \\
        t_l^n = \overline{x} - SD \cdot \lambda \\
        t_h^n = \overline{x} + SD \cdot \lambda
    \end{array}
\right.
$$, where $t_l^0$ corresponds to the low threshold at the first iteration, $t_l^n$ the low threshold at the n^th^ iteration, $t_j^0$ the high threshold at the first iteration, $t_j^n$ the high threshold at the n^th^ iteration, $\overline{x}$ the mean, $SD$ the standard deviation, $\lambda$ the distance inputted (default: 2.5).

---

## Median Absolute distance (MAD)

The median absolute distance method (MAD, `.method_MAD()`)  computes the threshold as the specified number of median absolute distance from the median. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l= med - MAD \cdot \lambda  \\
        t_h = med + MAD \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, $med$ the median, $MAD$ the median absolute distance, $\lambda$ the distance inputted (default: 2.5). An aberrant value is identified when it falls below the low threshold or exceeds the high threshold.

### What is MAD
The Median Absolute Deviation (MAD) is calculated as the median of the absolute distances from the overall median, multiplied by the scaling factor, b. Algorithmically, this involves computing the absolute difference between each value and the median, then determining the median of these absolute distances. The result is obtained by multiplying this median by the scaling factor, b = 1.4826, yielding the MAD. Formally,
$$MAD = b \cdot med(|x_i- med({x_j})|)$$, where $x_i$ corresponds to each value, $x_j$ the initial value, and b = 1.4826 if the distribution underlying value is normal.

---

## Method S~n~

The $S_n$ method (`.method_Sn()`) calculates a singular threshold corresponding to a specific distance from all other values. Formally,
$$t = S_n \cdot \lambda$$,  where $t$ corresponds to the threshold, and $\lambda$ the distance inputted (default: 2.5).

### What is S~n~
The $S_n$ method corresponds to the median of the distances between each point and every other point. Algorithmically, for each point, the absolute difference is computed from all other points and the median is realised on these distances. Subsequently, the median of these median distances is determined and multiplied by a constant, denoted as c, which is dependent on the participant number. You obtain the $S_n$. Formally,
$$S_n = c \cdot med_i\{med_j(x_i-x_j)\}$$, where $med_i$ corresponds to the median of each value distance, $med_j$ represents the median of distance between $x_i$ and $x_j$.

## Percentile
The percentile method (prctile, `.method_prctile()`) calculates the threshold as the value corresponding to both the specified percentile and its complement, 1 - percentile. More formally,
$$
\left\{
    \begin{array}{ll}
        t_l= 1 - percentile(\lambda)  \\
        t_h = percentile(\lambda)
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, percentile corresponds to the function (numpy) returning the value for a $\lambda$ value, input by the user.

## Cut-off

The cut-off method (cut-off, `.method_cutoff()`) is a special method where no threshold is computed. It is inputted directly by the user.

## Identical

The identical method (identical, `.method_identical()`) is special method too. Specifically, this method detects outliers if the frequency of same value is above a user-inputted frequency. It allows for example to detect if participant is always responding the same (for example "yes")
