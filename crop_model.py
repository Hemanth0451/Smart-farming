import joblib
import numpy as np

# Load trained model
model = joblib.load('crop_model.pkl')

# Example Input (N, P, K, temp, humidity, pH, rainfall)
sample_input = np.array([[90, 42, 43, 20.5, 80, 6.5, 200]])

# Predict crop
predicted_crop = model.predict(sample_input)
print(f"🌱 Recommended Crop: {predicted_crop[0]}")
