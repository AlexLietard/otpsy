import outliers_toolbox as ot
import pandas as pd

df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep = ";")

outliers = ot.Outliers(df, column = "all", participant_column= "CLI1")

outliers.__check_data_type()