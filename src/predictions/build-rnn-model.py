import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM,Dropout,Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout

def build_rnn_model():
    rcParams['figure.figsize']=20,10

    scaler=MinMaxScaler(feature_range=(0,1))

    df=pd.read_csv("./BTC-USD.csv")
    df.head()

    df["Date"]=pd.to_datetime(df.Date,format="%Y-%m-%d")
    df.index=df['Date']

    plt.figure(figsize=(16,8))
    plt.plot(df["Close"],label='Close Price history')

    data=df.sort_index(ascending=True,axis=0)
    new_dataset=pd.DataFrame(index=range(0,len(df)),columns=['Date','Close'])

    for i in range(0,len(data)):
        new_dataset["Date"][i]=data['Date'][i]
        new_dataset["Close"][i]=data["Close"][i]
        

    new_dataset.index=new_dataset.Date
    new_dataset.drop("Date",axis=1,inplace=True)

    final_dataset=new_dataset.values

    train_data=final_dataset[0:987,:]
    valid_data=final_dataset[987:,:]

    scaler=MinMaxScaler(feature_range=(0,1))
    scaled_data=scaler.fit_transform(final_dataset)

    x_train_data,y_train_data=[],[]

    for i in range(60,len(train_data)):
        x_train_data.append(scaled_data[i-60:i,0])
        y_train_data.append(scaled_data[i,0])
        
    x_train_data,y_train_data=np.array(x_train_data),np.array(y_train_data)

    x_train_data=np.reshape(x_train_data,(x_train_data.shape[0],x_train_data.shape[1],1))

    # # BUILD MODEL RNN
    rnn_model = Sequential()
    rnn_model.add(LSTM(units = 45, return_sequences = True, input_shape = (x_train_data.shape[1], 1)))
    rnn_model.add(Dropout(0.2))

    # #Adding three more LSTM layers with dropout regularization
    for i in [True, True, False]:
        rnn_model.add(LSTM(units = 45, return_sequences = i))
        rnn_model.add(Dropout(0.2))

    # #Adding our output layer
    rnn_model.add(Dense(units = 1))

    # #Compiling the recurrent neural network
    rnn_model.compile(optimizer = 'adam', loss = 'mean_squared_error')

    # #Training the recurrent neural network
    rnn_model.fit(x_train_data, y_train_data, epochs = 1, batch_size = 1)
    #rnn_model.fit(x_training_data, y_training_data, epochs = 100, batch_size = 32)

    # X_test
    inputs_data=new_dataset[len(new_dataset)-len(valid_data)-60:].values
    inputs_data=inputs_data.reshape(-1,1)
    inputs_data=scaler.transform(inputs_data)

    X_test=[]
    for i in range(60,inputs_data.shape[0]):
        X_test.append(inputs_data[i-60:i,0])
    X_test=np.array(X_test)
    X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

    # use model prediction
    closing_price=rnn_model.predict(X_test)
    closing_price=scaler.inverse_transform(closing_price)

    rnn_model.save("saved_btcusd_rnn_model.h5")