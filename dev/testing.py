import pandas as pd

df = pd.read_csv('C:/churn-intelligence-platform/data/2019-Oct.csv')
df.sample(500_000).to_csv('C:/churn-intelligence-platform/dev/sample.csv', index=False)
print("Done. Shape:", df.shape)