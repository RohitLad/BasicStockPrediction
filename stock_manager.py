import pandas as pd
import numpy as np
import pandas_datareader.data as web
import dateutil.relativedelta as date_rel
import datetime
import os


class stock_manager:

    historical_timeframe = 12*5 # 5 years
    end_date = datetime.date.today()
    start_date = end_date-date_rel.relativedelta(months=historical_timeframe)

    def __init__(self):
        self.portfolio = {}

    def insert_participant(self, name):
        stkr = stocker(name=name) 
        stkr.load_data(stock_manager.start_date, stock_manager.end_date)
        self.portfolio[name] = stkr

    def set_time_frame(self, start_date, end_date):
        for name in self.portfolio:
            self.portfolio[name].load_data(start_date,end_date)
    
    def combine_portfolios(self,key_val = 'Adj Close'):
        
        df = []
        for name in self.portfolio:
            s = self.portfolio[name].block_dataset[key_val]
            df.append((s.rename(name)))

        return pd.concat(df,axis=1,sort=False)

class stocker:
    _data_dir = 'data/'
    _data_ext = '.pkl'
    def __init__(self, name):
        self.name = name
        self.data_fname = stocker._data_dir + self.name + stocker._data_ext
        if os.path.isfile(self.data_fname):
            self.data = pd.read_pickle(self.data_fname)
        else:
            self.data = pd.DataFrame(columns=['Open','High','Low','Close','Volume','Adj Close'])
        self.pd_timestamp = pd._libs.tslibs.timestamps.Timestamp
        self.block_dataset = self.data

    def load_data(self, start_date, end_date):
        
        load_flag = True
        l_s = self.create_offset_days(current_day=start_date, window=3)
        l_e = self.create_offset_days(current_day=end_date, window=3, sign=-1)

        if_exists = False
        existing_dates = self.data.index

        if len(self.data) > 0:            
            if_exists,_,_ = self.check_if_days_exist(existing_dates,l_s,l_e)
        
        if not if_exists:
            self.data = web.DataReader(self.name,'yahoo',start_date,end_date)
            self.save_pickle()
        
        start_date = min(start_date,self.data.index.min())
        end_date = max(end_date,self.data.index.max())
        l_s = self.create_offset_days(current_day=start_date, window=3)
        l_e = self.create_offset_days(current_day=end_date, window=3, sign=-1)

        _,i,j = self.check_if_days_exist(self.data.index, l_s, l_e)
        self.block_dataset = self.data.loc[i:j,:]        

    def check_if_days_exist(self, existing_dates, start_list, end_list):
        for i in start_list:
            if i in existing_dates:
                for j in end_list:
                    if j in existing_dates:
                        return True, i, j
        return False, None, None
        
    def create_offset_days(self, current_day, window=3, sign=1):
        # In order to avoid sat sunday holiday stuff
        window = max(window,3)
        days = [current_day]
        for day in range(window):
            days.append(current_day+int(sign)*date_rel.relativedelta(days=day+1))
        return days

    def save_pickle(self):
        self.data.to_pickle(self.data_fname)

    def moving_average(self, window = 10, key_val = 'Adj Close'):
        return self.block_dataset[key_val].rolling(window=window).mean()

    def return_deviation(self, key_val = 'Adj Close'):
        return self.block_dataset[key_val]/self.block_dataset[key_val].shift(1) - 1.0

