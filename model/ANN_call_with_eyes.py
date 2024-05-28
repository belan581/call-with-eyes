import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

# Paso 3: Cargar el dataset
dataset = pd.read_csv("distances.csv")
X = dataset.iloc[:, :54].values  # Valores de las distancias
y = dataset.iloc[:, 54].values  # Etiquetas

# Opcional: Normalizar los datos
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Convertir etiquetas a one-hot encoding
y = to_categorical(y)

# Dividir el dataset en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Paso 4: Construir el modelo
model = Sequential(
    [
        Dense(10, activation="relu", input_shape=(X_train.shape[1],)),
        Dense(10, activation="relu"),
        Dense(y.shape[1], activation="softmax"),
    ]
)

# Paso 5: Compilar el modelo
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Paso 6: Entrenar el modelo
model.fit(X_train, y_train, epochs=100, batch_size=10)

# Paso 7: Evaluar el modelo
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Loss: {loss}, Accuracy: {accuracy}")

# Guardar el modelo
model.save("model/modelo_call_with_eyes.h5")

# Guardar el scaler del entrenamiento
joblib.dump(scaler, "model/scaler_entrenamiento.pkl")
