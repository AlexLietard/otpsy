# It is important to run "pip install -e ." before running test

import pandas as pd
import numpy as np
import pytest
import otpsy as ot

df = pd.read_csv("./tests/data.csv", sep=";")
class TestClass:
    sample_columns_to_test_p_col = \
            ot.Sample(df, 
                        columns_to_test=["art_looking_time", "discrimination_performance"], 
                        id_column="index_participant")
    outliers = sample_columns_to_test_p_col.method_tukey(distance=2.4, threshold_included=True)

    def test_Instantiation(self):
        self.sample_columns_to_test_p_col.method_tukey()
        self.sample_columns_to_test_p_col.method_tukey(distance = 2.4)
        self.sample_columns_to_test_p_col.method_tukey(threshold_included=True)

    def test_verify_dict_col(self):
        dict_col = {'art_looking_time': ['P10', 'P11'], 'discrimination_performance': ['P37']}
        assert(self.outliers.dict_col == dict_col)

    def test_verify_all_index(self):
        all_index = ['P10', 'P11', 'P37']
        assert(self.outliers.all_index == all_index)

    def test_verify_nb(self):
        nb = {'art_looking_time': 2, 'discrimination_performance': 1}
        assert(self.outliers.nb == nb)

    def test_verify_position(self):
        position = {'art_looking_time': [9, 10], 'discrimination_performance': [36]}
        assert(self.outliers.position == position)
    
    def test_threshold_value(self):
        threshold = {'art_looking_time': (413.15908782306656, 3418.637601951734), 
                     'discrimination_performance': (0.6575295009176081, 1.1263237685404994)}
        assert(self.outliers.threshold == threshold)
    
    def test_add_method(self):
        self.outliers.add("P8")
        assert(self.outliers.dict_col == 
                {'art_looking_time': ['P10', 'P11'], 
                 'discrimination_performance': ['P37'],
                 "added_manually": ["P8"]}
                 )
        assert(self.outliers.position == 
               {'art_looking_time': [9, 10], 
                'discrimination_performance': [36],
                "added_manually":[7]}
                )
        assert(self.outliers.nb ==
               {'art_looking_time': 2, 'discrimination_performance': 1, "added_manually":1})
        assert(self.outliers.all_index == ["P10", "P11", "P37", "P8"])

    def test_remove_method(self):
        self.outliers.remove("P10")
        assert(self.outliers.dict_col ==
                {'art_looking_time': ['P11'], 
                 'discrimination_performance': ['P37'],
                 "added_manually": ["P8"]}
                 )
        assert(self.outliers.position == 
               {'art_looking_time': [10], 
                'discrimination_performance': [36],
                "added_manually":[7]}
                )
        assert(self.outliers.nb ==
               {'art_looking_time': 1, 'discrimination_performance': 1, "added_manually":1})
        assert(self.outliers.all_index == ["P11", "P37", "P8"])

    def test_manage_method(self):
        df1 = self.outliers.manage(method="delete")
        assert(len(df1.index) == 57)

        df2 = self.outliers.manage(method = "winsorise")
        assert(df2.loc["P11", "art_looking_time"] == self.outliers.threshold["art_looking_time"][0])

        df3 = self.outliers.manage(method = "na")
        assert(np.isnan(df3.loc["P11", "art_looking_time"]))