import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM,Dropout,Dense
from datetime import datetime
from keras.models import load_model
from common.helpers import date_to_milliseconds


def lstm_prediction_process(_isReset):
    rcParams['figure.figsize']=20,10

    scaler=MinMaxScaler(feature_range=(0,1))

    df=pd.read_csv("BTC-USD.csv")
    df.head()

    df["Date"]=pd.to_datetime(df.Date,format="%Y-%m-%d %H:%M:%S", utc=False)
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

    train_size = int(len(df) * 0.9)
    train_data=final_dataset[0:train_size,:]
    valid_data=final_dataset[train_size:,:]

    scaler=MinMaxScaler(feature_range=(0,1))
    scaled_data=scaler.fit_transform(final_dataset)

    x_train_data,y_train_data=[],[]

    for i in range(60,len(train_data)):
        x_train_data.append(scaled_data[i-60:i,0])
        y_train_data.append(scaled_data[i,0])
        
    x_train_data,y_train_data=np.array(x_train_data),np.array(y_train_data)

    x_train_data=np.reshape(x_train_data,(x_train_data.shape[0],x_train_data.shape[1],1))

    # Tạo X test để dự đoán
    inputs_data=new_dataset[len(new_dataset)-len(valid_data)-60:].values
    inputs_data=inputs_data.reshape(-1,1)
    inputs_data=scaler.transform(inputs_data)

    X_test=[]
    for i in range(60,inputs_data.shape[0]):
        X_test.append(inputs_data[i-60:i,0])
    X_test=np.array(X_test)
    X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

    # Kiểm tra build lại model
    if _isReset:
        # BUILD MODEL LSTM
        lstm_model=Sequential()
        lstm_model.add(LSTM(units=50,return_sequences=True,input_shape=(x_train_data.shape[1],1)))
        lstm_model.add(LSTM(units=50))
        lstm_model.add(Dense(1))

        lstm_model.compile(loss='mean_squared_error',optimizer='adam')
        lstm_model.fit(x_train_data,y_train_data,epochs=1,batch_size=1,verbose=2)

        # lưu model
        lstm_model.save("saved_btcusd_lstm_model.h5")
        # cập nhật file lastDate
        _now = datetime.now().strftime("%Y-%m-%d")
        w_file = open("lastDate.txt", "w")
        w_file.write(_now)
        w_file.write(" 23:59:59")
        w_file.close()


    # Load saved model
    lstm_model=load_model("saved_btcusd_lstm_model.h5")

    closing_price=lstm_model.predict(X_test)
    closing_price=scaler.inverse_transform(closing_price)

    train_data=new_dataset[:train_size]
    valid_data=new_dataset[train_size:]
    valid_data['Predictions']=closing_price


    _returnData = []
    for i in range(0, len(valid_data)):
        _returnData.append({
            "value": float(valid_data['Predictions'][i]),
            "time": date_to_milliseconds(valid_data.index[i].strftime("%Y-%m-%d %H:%M:%S")) / 1000
        })

    return _returnData