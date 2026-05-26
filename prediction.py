from sklearn.linear_model import LinearRegression
import numpy as np

sizes = np.array([1000, 1500, 2000, 2500, 3000]).reshape(-1,1)
prices = [160000, 210000, 240000, 310000, 350000]

model = LinearRegression()
model.fit(sizes,prices)

predicted_price = model.predict([[3500]])
print(f"Predicted price: ${predicted_price[0]:,.2f}")

