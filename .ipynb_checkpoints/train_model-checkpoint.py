import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Load data
df = pd.read_csv('data.csv')
X = df[['area', 'bedrooms', 'bathrooms', 'age']]
y = df['price']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved as model.pkl")
