import pandas as pd
import numpy as np
import datetime
import pandas_datareader.data as web
import dateutil.relativedelta as date_rel
import matplotlib.pyplot as plt
from matplotlib import style
import os

historical_timeframe = 12*3 # always provide in months
historical_timeframe = int(historical_timeframe)

end_date = datetime.date.today()
start_date = end_date - date_rel.relativedelta(months=historical_timeframe)


stock_names = ['AAPL','TSLA','GOOG','MSFT']



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
        self.begin_date = self.pd_timestamp(self.data.index.min())
        self.end_date = self.pd_timestamp(self.data.index.max())
        self.time_frame = {'begin':self.begin_date, 'end':self.end_date}
        self.block_dataset = self.data

    def load_data(self, start_date, end_date):
        
        load_flag = True
        s1,s2,s3,s4 = self.create_offset_days(current_day=start_date, window=3)
        e1,e2,e3,e4 = self.create_offset_days(current_day=end_date, window=3, sign=-1)
        
        if len(self.data) > 0:
            existing_dates = self.data.index

            if (s1 in existing_dates or s2 in existing_dates or s3 in existing_dates or s4 in existing_dates):
                if (e1 in existing_dates or e2 in existing_dates or e3 in existing_dates or e4 in existing_dates):
                    load_flag = False
            else:
                start_date = min(start_date,end_date,self.begin_date)
                end_date = max(start_date,end_date,self.end_date)
        
        if load_flag:
            self.data = web.DataReader(self.name,'yahoo',start_date,end_date)
            self.save_pickle()

        existing_dates = self.data.index
        l_s = [s1,s2,s3,s4]
        l_e = [e1,e2,e3,e4]
        for i in l_s:
            if i in existing_dates:
                for j in l_e:
                    if j in existing_dates:
                        self.block_dataset = self.data.loc[i:j,:]
        
    def create_offset_days(self, current_day, window=3, sign=1):
        # In order to avoid sat sunday holiday stuff
        window = max(window,3)
        days = (current_day,)
        for day in range(window):
            days+=(current_day+int(sign)*date_rel.relativedelta(days=day+1),)
            #days.append(current_day+date_rel.relativedelta(days=day+1))
        return days

    def save_pickle(self):
        self.data.to_pickle(self.data_fname)

    def moving_average(self, window = 10, key_val = 'Adj Close'):
        return self.block_dataset[key_val].rolling(window=window).mean()

    def return_deviation(self, key_val = 'Adj Close'):
        return self.block_dataset[key_val]/self.block_dataset[key_val].shift(1) - 1.0

aapl = stocker(name='AAPL')
aapl.load_data(start_date=start_date,end_date=end_date)
ak = 0

plt.plot(aapl.return_deviation(),'r-')
#plt.plot(aapl.block_dataset['Adj Close'],'r-')
#plt.plot(aapl.moving_average(window=50),'b-')
plt.show()
