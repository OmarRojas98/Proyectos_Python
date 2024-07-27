import numpy as np

def Initialize_model(vector):
  w = np.zeros(vector.shape[1])
  b= 0
  return w,b

def loss(y, y_hat):
    loss = -np.mean(y*(np.log(y_hat)) + (1-y)*np.log(1-y_hat))
    return loss

def gradients(X, y, y_hat):
    # X --> Input.
    # y --> true/target value.
    # y_hat --> predictions.
    # w --> weights (parameter).
    # b --> bias (parameter).
    # m-> number of training examples.
    m = X.shape[0]
    # Gradient of loss w.r.t weights.
    dw = np.dot(X.T, (y_hat - y))/m  # revisar el signo
    # Gradient of loss w.r.t bias.
    db = sum(y_hat - y)/m
    return dw, db


def predict_prob(X, w, b):

    # X --> Input with all data, X is matrix with each column contains one data.
    predict_prob = sigmoid(np.dot(X,w) + b)

    return np.array(predict_prob)

def predict_class__no(X,w,b):
    # X --> Input with all data, X is matrix with each column contains one data.
    predict = sigmoid(X*w + b)
    TH = 0.5 # threshold
    # if y_hat >= 0.5 --> round up to 1
    # if y_hat < 0.5 --> round up to 10
    predict_class = [1 if i > TH else 0 for i in predict.shape]
    return np.array(predict_class)

def predict_class(X, w, b):
    z = np.dot(X, w) + b
    h = sigmoid(z)
    return (h >= 0.5).astype(int)

def sigmoid(z):
    return 1/(1 + np.exp(-z))


def accuracy(y, y_predict_class):
    accuracy = np.sum(y == y_predict_class) / len(y)
    return accuracy