import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from keras.models import load_model
from common.helpers import date_to_milliseconds

def xgb_prediction_process(_isReset):
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
        
    train_size = int(len(df) * 0.9)
    new_dataset.index=new_dataset.Date
    new_dataset.drop("Date",axis=1,inplace=True)

    ################################################################
    raw_df = new_dataset

    data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :0]])
    target = raw_df.values[1::2, 0]

    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.2, random_state=123)

    # Khởi tạo DMatrix cho XGBoost
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    if _isReset:
        # Thiết lập các tham số cho XGBoost
        param = {
            'max_depth': 3,
            'eta': 0.3,
            'objective': 'reg:squarederror'}

        # Huấn luyện mô hình XGBoost
        num_round = 100
        bst = xgb.train(param, dtrain, num_round)

        # Lưu model
        bst.save_model("saved_btcusd_xgb_model.bin")

        # cập nhật file lastDate
        _now = datetime.now().strftime("%Y-%m-%d")
        w_file = open("lastDate.txt", "w")
        w_file.write(_now)
        w_file.write(" 23:59:59")
        w_file.close()

    # Load saved model
    # xgb_model=load_model("saved_btcusd_xgb_model.h5")
    xgb_model = xgb.Booster()
    xgb_model.load_model('saved_btcusd_xgb_model.bin')

    # Dự đoán kết quả trên tập kiểm tra
    closing_price = xgb_model.predict(dtest)

    valid_data=new_dataset[train_size:]
    valid_data['Predictions']=closing_price

    _returnData = []
    for i in range(0, len(valid_data)):
        _returnData.append({
            "value": float(valid_data['Predictions'][i]),
            "time": date_to_milliseconds(valid_data.index[i].strftime("%Y-%m-%d %H:%M:%S")) / 1000
        })

    return _returnData