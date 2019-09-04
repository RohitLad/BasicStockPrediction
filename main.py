
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
for name in stock_names:
    manager.insert_participant(name=name)

manager.set_time_frame(start_date=start_date,end_date=end_date)
combined = manager.combine_portfolios()
returns = combined.pct_change()

plt.scatter(returns['AAPL'],returns['GOOG'])
plt.show()