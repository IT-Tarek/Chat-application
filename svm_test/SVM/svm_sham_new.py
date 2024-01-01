import pandas as pd
from sklearn.impute import SimpleImputer
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score

# ------------------------load data--------------------


dataset = pd.read_excel(
    r'C:\Users\tarek\Desktop\test_test\prpject_7\sham12.xlsx', encoding='utf-8-sig')
dataset = dataset.dropna()
dataset = dataset.reset_index(drop=True)

X = dataset.iloc[:, 0]
y = dataset.iloc[:, 1]

print('x >>>>>\n : ', X)
print('y >>>>>: \n', y)


# ------------------------data split--------------------


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=44, shuffle=True)


# ------------------------tfidf--------------------
count_vect = TfidfVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
X_train_counts.toarray()

X_test_counts = count_vect.fit_transform(X_test)
X_test_counts.toarray()

dataframe = pd.DataFrame(X_train_counts.toarray())
print(dataframe)


#print("------------------SVM--------------------- ")


SVCModel = SVC(kernel='rbf',    max_iter=100, C=2.0, gamma='auto')

SVCModel.fit(X_train_counts, y_train)


# score
print('SVCModel Train Score is : ', SVCModel.score(X_train_counts, y_train))
SVCModel.fit(X_test_counts, y_test)

print('SVCModel Test Score is : ', SVCModel.score(X_test_counts, y_test))


# Calculating Prediction
y_pred = SVCModel.predict(X_test_counts)
print('Predicted Value for SVCModel is : ', y_pred[:10])

# ----------------------------------------------------
# Calculating Confusion Matrix
CM = confusion_matrix(y_test, y_pred)
print('Confusion Matrix is : \n', CM)