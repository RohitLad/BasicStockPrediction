
import matplotlib.pyplot as plt
from matplotlib import style
from stock_manager import stock_manager
import datetime
import dateutil.relativedelta as date_rel


historical_timeframe = 12 # always provide in months
historical_timeframe = int(historical_timeframe)
end_date = datetime.date.today()
start_date = end_date - date_rel.relativedelta(months=historical_timeframe)
stock_names = ['AAPL','TSLA','GOOG','MSFT']
stock_dict = {}

manager = stock_manager()
manager.insert_ticker(names=stock_names)
manager.set_time_frame(start_index=int(manager.size_database*0.5),days=500)

mvs = manager.moving_average(window=15)

training_set = manager.generate_training_sets()
manager.n_order_regression(dataset=training_set,order=2)