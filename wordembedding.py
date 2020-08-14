# -*- coding: utf-8 -*-
"""WordEmbedding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1osh7IQ4m1RtNzgp2_T2a89PzXC3bTu5M
"""

!pip install -qq dask

# Importing the required libraries
import os
import numpy as np
from tensorflow.keras import layers
import tensorflow as tf
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras import models
from tensorflow.keras.preprocessing import text
import warnings
warnings.filterwarnings('ignore')
from sklearn import model_selection
from sklearn import metrics

import pandas as pd
import dask.dataframe as dd

# Connecting to Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Reading the DataSet
path = '/content/drive/My Drive/DataSets'

sms = pd.read_csv(os.path.join(path,"spam.csv"), encoding='latin-1')
sms.dropna(how="any", inplace=True, axis="columns")
sms.columns = ['label', 'message']
sms.head()

# Describing the Dataset
sms.describe()

# Doing some basic exploration
sms.groupby('label').describe()

sms['label_num'] = sms.label.map({'ham':0,'spam':1})
sms['message_len'] = sms.message.apply(len)
sms.head()

sms.describe()

sms[sms.message_len == 910].message.iloc[0]

# Cleaning and doing some preliminary operations
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
nltk.download('stopwords')
nltk.download('wordnet')

def text_process(mess):
    STOPWORDS = stopwords.words('english') + ['u', 'ü', 'ur', '4', '2', 'im', 'dont', 'doin', 'ure']
    nopunc = [char for char in mess if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return  ' '.join([word for word in nopunc.split() if word.lower() not in STOPWORDS])
    # return ' '.join([lemmatizer.lemmatize(word) for word in nopunc.split()])

sms['clean_msg'] = sms.message.apply(text_process)

sms.drop(['label','message','message_len'],inplace=True,axis='columns')
sms['message_len'] = sms.clean_msg.apply(len)
sms.head()

print(sms.message_len.sort_values(ascending=False).head(10))
sms.message_len.sort_values(ascending=False).head(10).plot(kind ='bar')

# separating indipendent and dependent variable
X = sms.clean_msg
y = sms.label_num.values

# Doing one how encoding step required for word embedding
vocab_size = 100000
onehot_repr=[text.one_hot(words,vocab_size)for words in X] 
print(onehot_repr)

# Padding the sentence to make it same length
sent_length = 520
embedded_docs=sequence.pad_sequences(onehot_repr,padding='pre',maxlen=sent_length)
print(embedded_docs)

# Splitting the Data int0 train and test
X_train,X_test,y_train,y_test = model_selection.train_test_split(embedded_docs,y,test_size=0.2,random_state=42)

# Creating a very basic model as the idea for this notebook is to start with  the embedding layer
dim = 50
model=models.Sequential()
model.add(layers.Embedding(vocab_size,dim,input_length=sent_length))
model.add(layers.Flatten())
model.add(layers.Dense(32, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
model.summary()

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['acc'])

history = model.fit(X_train, y_train,
                    epochs=10,
                    batch_size=32,
                    validation_data=(X_test, y_test))

# Plotting the  accuracy for train and test
from matplotlib import pyplot as plt
plt.figure(figsize=(10,5))
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.show()

# Plotting the loss for train and test
from matplotlib import pyplot as plt
plt.figure(figsize=(10,5))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.show()

# Using base metrics for the validation
prediction = model.predict(X_test).reshape(-1,)
# prediction = [1 if x>0.5 else 0 for x in prediction]

l1 = [i/100 for i in range(10,110,10)]
for i in l1:
  pred = [1 if x>i else 0 for x in prediction]
  con_mat = metrics.confusion_matrix(y_test,pred)
  print(i,con_mat[1,0])

prediction = [1 if x>0.3 else 0 for x in prediction]
print(metrics.classification_report(y_test,prediction))

metrics.confusion_matrix(y_test,prediction)

