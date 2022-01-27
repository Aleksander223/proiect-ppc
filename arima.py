import pandas as pd
from itertools import product

from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=ConvergenceWarning)


def optimize_ARIMA(generated_list, exog):
    best = []
    best_aic = -1
    for order in generated_list[0]:
        for order_seasonal in generated_list[1]:
            try:
                model = SARIMAX(exog, order=order, seasonal_order=order_seasonal, enforce_stationarity=False,
                                enforce_invertibility=False).fit(disp=False)
            except ValueError:
                print("Eroare ARIMA", order)
                continue
            if model.aic < best_aic or best_aic == -1:
                best_aic = model.aic
                best = [order, order_seasonal, model.aic]

    return best


def generate_parameters(max_d=1, max_ar=3, max_ma=3):
    ps = range(0, max_ar)
    d = range(0, max_d)
    qs = range(0, max_ma)

    parameters_list = list(product(ps, qs))
    order_list = []

    for d_i in d:
        for each in parameters_list:
            each = list(each)
            each.insert(1, d_i)
            each = tuple(each)
            order_list.append(each)

    seasonal_pdq = [(y[0], y[1], y[2], 12) for y in order_list]
    return order_list, seasonal_pdq


def predict(data, days_prediction_input):
    date_cols = ['year', 'mo', 'da']
    important_cols = ['date', 'temp']

    data['date'] = data[date_cols].apply(lambda row: pd.to_datetime('-'.join(row.values.astype(str))).date(), axis=1)

    temp_df = data[important_cols]

    mask = (temp_df.date >= pd.to_datetime('2018-01-01').date()) & (temp_df.date <= pd.to_datetime('2021-12-31').date())
    temp_df = temp_df.loc[mask]

    my_range = pd.date_range(start=min(temp_df.date), end=max(temp_df.date), freq='B')
    temp_mean = temp_df['temp'].mean()
    for x in my_range.difference(temp_df.date):
        temp_df = pd.concat([temp_df, pd.DataFrame([[x, temp_mean]], columns=['date', 'temp'])])

    temp_df.index = pd.DatetimeIndex(temp_df.date).to_period('D')
    temp_df = temp_df.sort_index()

    N = len(data.temp)
    split = 1
    training_size = round(split * N)

    train_series = temp_df.temp[:training_size]

    result = optimize_ARIMA(generate_parameters(), exog=train_series)

    best_model = SARIMAX(train_series, order=result[0], seasonal_order=result[1], enforce_stationarity=False,
                         enforce_invertibility=False).fit(disp=False)

    pred = best_model.get_prediction(start=pd.to_datetime('2022-01-01'),
                                     end=pd.to_datetime('today') + pd.DateOffset(days=days_prediction_input),
                                     dynamic=False)
    result = pred.predicted_mean
    return result[-days_prediction_input:]
