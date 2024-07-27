import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons # Make a sintetic dataset
from sklearn.datasets import make_classification
import fuctions as f

################################################################################################################
# Generate some Sintetic data
n_samples = 1000
X, y = make_moons(n_samples=n_samples, noise=0.5, random_state=1)
# Plot the data
plt.plot(X[:, 0][y==0], X[:, 1][y==0], "go")
plt.plot(X[:, 0][y==1], X[:, 1][y==1], "ro")
plt.xlabel("feature 1")
plt.ylabel("feature 2")

############################ separamos los datos en 80/20 teniendo 80% de los datos para entrenar

split_size = round(n_samples*0.8)

X_train = X[:split_size]
y_train = y[:split_size]

X_test = X[split_size:]
y_test = y[split_size:]
################################################################################################################


losses = []
#losses.append(loss)

w,b = f.Initialize_model(X_train)
alpha = 0.001

for i in range(0,100000):
  y_hat = f.predict_prob(X_train, w, b)
  dw , db = f.gradients(X_train, y_train, y_hat)
  w = w-alpha*dw
  b = b-alpha*db
y_predict_class = f.predict_class(X_train,w,b)
acc = f.accuracy(y_train,y_predict_class)

print(w,b,acc)