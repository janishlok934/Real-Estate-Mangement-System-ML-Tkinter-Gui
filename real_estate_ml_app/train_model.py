import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Fake training data
data = {
    'Area': [1000, 1500, 2000, 2500, 3000],
    'Bedrooms': [2, 3, 3, 4, 4],
    'Bathrooms': [1, 2, 2, 3, 3],
    'Age': [10, 5, 7, 3, 1],
    'Price': [5000000, 7500000, 9500000, 12500000, 15000000]
}

df = pd.DataFrame(data)

X = df[['Area', 'Bedrooms', 'Bathrooms', 'Age']]
y = df['Price']

model = LinearRegression()
model.fit(X, y)

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
