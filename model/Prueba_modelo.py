import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib

# Cargar el modelo desde el archivo
model = load_model("modelo_call_with_eyes.h5")

# Cargar el scaler
scaler = joblib.load("scaler_entrenamiento.pkl")


# Leer el archivo .csv
data = pd.read_csv("distances.csv")

# Seleccionar una muestra (puedes cambiar el índice para elegir otra fila)
sample = data.iloc[675]  # Elegir la primera fila, por ejemplo

# Separar las características (entradas) y la etiqueta
X_sample = sample[:54].values  # Las primeras 54 columnas son las características
y_true = sample[54]  # La columna 55 es la etiqueta (verdadera)

# Redimensionar la muestra para que tenga la forma correcta
X_sample = np.expand_dims(X_sample, axis=0)

# Normalizar la muestra usando el scaler
X_sample_normalized = scaler.transform(X_sample)

# Hacer la predicción
y_pred = model.predict(X_sample_normalized)

# Si es una clasificación, podrías querer obtener la clase con mayor probabilidad
predicted_class = np.argmax(y_pred, axis=1)

print(f"Predicción del modelo: {predicted_class[0]}")
print(f"Etiqueta verdadera: {y_true}")
