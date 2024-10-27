import pandas as pd
import os 
import pytest
df = pd.read_csv("./tests/data.csv", sep=";")

# Allow to have the local copy of package
os.chdir("./src")
import otpsy as ot

@pytest.mark.parametrize("df", [df])
class TestClass:
    def test_sample_instantiation(self, df):
        sample_two_cols = \
            ot.Sample(df[["age", "random_col"]])
        
        sample_columns_to_test = \
            ot.Sample(df, columns_to_test="age")
        
        sample_columns_to_test = \
            ot.Sample(df, columns_to_test=["age", "random_col"])
        
        sample_columns_to_test_number_unique = \
            ot.Sample(df, columns_to_test=3)
        
        sample_columns_to_test_number = \
            ot.Sample(df, columns_to_test=[3, 4])         
        
        sample_columns_to_test_p_col = \
            ot.Sample(df, columns_to_test=["age", "random_col"], participant_column="index_participant")

        sample_columns_to_test_p_col = \
            ot.Sample(df, columns_to_test=["age", "random_col"], participant_column=1)

os.chdir("..")
