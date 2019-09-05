
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
manager.set_time_frame(start_index=int(manager.size_database*0.5),days=100) # how many days should be present in the considered timeframe

mvs = manager.moving_average(window=15)

training_set = manager.generate_training_sets(ratio=0.2) # ratio is the percentage of the number of days (look the above comment) which will be predicted
# ratio = .2 for 100 days would mean that 20 days will be predicted 
linreg = manager.linear_regression(dataset=training_set)
quad = manager.n_order_regression(dataset=training_set, order=2)
cube = manager.n_order_regression(dataset=training_set,order=3)

fitnesses = {'Linear': linreg, 'Poly 2': quad, 'Poly 3': cube}

for reg in fitnesses:
    fig = plt.figure()
    fig.suptitle(reg)
    n_stocks = len(fitnesses[reg])
    count=1
    for stock_name in fitnesses[reg]:
        fit_func = fitnesses[reg][stock_name]
        predictions = fit_func.predict(training_set[stock_name]['X_lately'])
        unscaled_original = list(training_set[stock_name]['X']*training_set[stock_name]['std']+training_set[stock_name]['mean'])
        original_dates = list(training_set[stock_name]['X_dates'])
        unscaled_predictions = [unscaled_original[-1]]
        unscaled_predictions.extend(list(predictions*training_set[stock_name]['std']+training_set[stock_name]['mean']))
        prediction_dates = [original_dates[-1]]
        prediction_dates.extend(list(training_set[stock_name]['Xl_dates']))
        ax = fig.add_subplot(n_stocks,1,count)
        ax.set_title(stock_name)
        plt.plot_date(original_dates,unscaled_original,'b-')
        plt.plot_date(prediction_dates,unscaled_predictions,'r-')
        ax.tick_params(axis='x', rotation=15)
        count+=1
plt.show()