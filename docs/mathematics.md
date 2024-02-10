# Mathematical description

This file is used to present mathematically what each method is computing.

## Interquartile range (IQR)

The interquartile range (IQR, `.method_IQR()`) method computes threshold as a specified number of interquartile range from the median. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = med - IQR \cdot \lambda \\
        t_h = med + IQR \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, $med$ corresponds to the median, $IQR$ corresponds to $Q3-Q1$, and $\lambda is the distance inputted by user (default: 2).
A value is outlier if it lies below or above the low threshold or the high threshold respectively.

---

## Tukey (tukey)

The Tukey (tukey, `.method_tukey()`) method computes threshold as a specified number of interquartile range from the first quartile or the third quartile. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = Q1 - IQR \cdot \lambda \\
        t_h = Q3 + IQR \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold, $Q1$ the first quartile, $Q3$ the third quartile, $\lambda$ the distance inputted (default: 1.5). A value is outlier if it lies below or above the low threshold or the high threshold respectively.

---

## Standard deviation (SD)

The Standard deviation (SD, `.method_SD()`) method computes the threshold as a specified number of standard deviation from the mean. Formally,
$$
\left\{
    \begin{array}{ll}
        t_l = \overline{x} - SD \cdot \lambda \\
        t_h = \overline{x} + SD \cdot \lambda
    \end{array}
\right.
$$, where $t_l$ corresponds to the low threshold, $t_h$ the high threshold,$\overline{x}$ the mean, $SD$ the standard deviation, $\lambda$ the distance inputted (default: 2.5). A value is outlier if it lies below or above the low threshold or the high threshold respectively.

---

## Recursive standard deviation (rSD)

The recursive standard deviation (rSD, `.method_rSD()`) method compute the threshold as the specified number of standard deviation (default: 3) from the mean, and continue to compute the threshold until there is no outlier or the maximal iteration is reached (default: 3). Formally,
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

...
