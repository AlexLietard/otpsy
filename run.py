import outliers_toolbox
import pandas as pd

df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep = ";")

outliers = outliers_toolbox.Outliers("df", "premiere_lettre_nombre")
