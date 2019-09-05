import pandas as pd
import numpy as np
import pandas_datareader.data as web
import dateutil.relativedelta as date_rel
import datetime
import os
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import PolynomialFeatures, scale
from sklearn.pipeline import make_pipeline

class stock_manager:

    historical_timeframe = 12*5 # 5 years
    end_date = datetime.date.today()
    start_date = end_date-date_rel.relativedelta(months=historical_timeframe)

    def __init__(self):
        self.portfolio = {}

    @property
    def size_database(self):
        f_name = list(self.portfolio.keys())[0]
        return len(self.portfolio[f_name].data)

    def insert_ticker(self, names):
        if type(names) is str:
            names=[names]
        for name in names:
            self.portfolio[name] = stocker(name=name)

    def set_time_frame(self, start_date=None, start_index=0, days=50):
        if start_date:
            f_name = list(self.portfolio.keys())[0]
            assert(start_date in self.portfolio[f_name].data.index)
            start_index = self.portfolio[f_name].data.index.get_loc(start_date)
        for name in self.portfolio:
            self.portfolio[name].create_chunk(index=start_index,days=days)
    
    def combine_portfolios(self,key_val = 'Adj Close'):
        
        df = []
        for name in self.portfolio:
            s = self.portfolio[name].block_dataset[key_val]
            df.append((s.rename(name)))

        return pd.concat(df,axis=1,sort=False)

    def moving_average(self,window = 10, key_val='Adj Close'):
        val = {}
        for name in self.portfolio:
            val[name]=self.portfolio[name].moving_average(window = window, key_val =key_val)
        return val

    def generate_training_sets(self,ratio=0.05):
        val = {}
        for name in self.portfolio:
            X,y,X_new,mean,var,X_dates,Xl_dates = self.portfolio[name].generate_training_sets(ratio=ratio)
            val[name]={'X':X,'y':y,'X_lately':X_new,'mean':mean,'std':var,'X_dates':X_dates,'Xl_dates':Xl_dates}
        return val

    def linear_regression(self, dataset):
        val = {}
        for name in dataset:
            linreg = LinearRegression(n_jobs=-1)
            linreg.fit(dataset[name]['X'],dataset[name]['y'])
            val[name]=linreg
        return val

    def n_order_regression(self, dataset, order=2):
        val = {}
        for name in dataset:
            reg = make_pipeline(PolynomialFeatures(order), Ridge())
            reg.fit(dataset[name]['X'],dataset[name]['y'])
            val[name]=reg
        return val

class stocker:
    _data_dir = 'data/'
    _data_ext = '.pkl'
    def __init__(self, name):
        self.name = name
        self.data_fname = stocker._data_dir + self.name + stocker._data_ext
        today = stock_manager.end_date
        if os.path.isfile(self.data_fname):
            self.data = pd.read_pickle(self.data_fname)
            start_date = self.data.index[-1]
        else:
            self.data = pd.DataFrame(columns=['Open','High','Low','Close','Volume','Adj Close'])
            start_date = stock_manager.start_date

        extra_data = []#self.load_from_web(start_date=start_date, end_date=today)
        if len(extra_data)>0:
            self.data = pd.concat([self.data,extra_data],axis=0)
            self.save_pickle()

        self.block_dataset = self.data

    def load_from_web(self,start_date,end_date):
        return web.DataReader(self.name,'yahoo',start_date,end_date)

    def create_chunk(self, days=30,random=False,index=0):
        if random:
            index = np.random.randint(low=0,high=len(self.data)-days)
        else:
            assert(len(self.data)-days>=index)
        
        self.block_dataset = self.data.iloc[index:index+days]
        
    def save_pickle(self):
        self.data.to_pickle(self.data_fname)

    def moving_average(self, window = 10, key_val = 'Adj Close'):
        return self.block_dataset[key_val].rolling(window=window).mean()

    def return_deviation(self, key_val = 'Adj Close'):
        return self.block_dataset[key_val]/self.block_dataset[key_val].shift(1) - 1.0

    def generate_training_sets1(self,ratio = 0.01, key_val='Adj Close'):
        dataset = self.block_dataset.copy(deep=True)
        forecast_out = int(np.ceil(ratio*len(dataset)))
        dataset['label'] = dataset[key_val].shift(-forecast_out)
        X = np.array(dataset.drop(['label'],1))
        X = scale(X)
        X_lately = X[-forecast_out:]
        X = X[:-forecast_out]
        y=np.array[dataset['label']]
        y=y[:-forecast_out]
        return X,y,X_lately

    def generate_training_sets(self,ratio = 0.01, key_val='Adj Close'):
        dataset = self.block_dataset.copy(deep=True)
        forecast_out = int(np.ceil(ratio*len(dataset)))
        removed_chunk = dataset[key_val]
        X = np.array(removed_chunk)
        mean = X.mean()
        var = X.std()
        X_dates = dataset.index[0:-forecast_out]
        Xl_dates = dataset.index[-forecast_out:]
        X = scale(X)
        y = X[forecast_out:]
        X_lately = X[-forecast_out:].reshape(-1,1)
        X = X[:-forecast_out].reshape(-1,1)
        return X,y,X_lately,mean,var,X_dates,Xl_dates

if __name__=='__main__':
    ak = stocker(name='AAPL')
    ak.create_chunk(days=2,random=True)