#!/usr/bin/env python

import pandas as pd
from cvts import calculate_base

data_file = '../test/test.csv'
df = pd.read_csv(data_file)
res = calculate_base(
    df['Longitude'],
    df['Latitude'],
    df['speed'])
print(res)
