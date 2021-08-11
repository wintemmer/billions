import pandas as pd

def monthly(data, type='first'):
    data = pd.DataFrame(data)
    data.columns = ['date']
    data['year'] = data['date'].apply(lambda x: x.year)
    data['month'] = data['date'].apply(lambda x: x.month)
    grouped = data['date'].groupby([data['year'], data['month']])
    if type=='first':
        last_day = grouped.min().to_list()
    elif type=='last':
        last_day = grouped.max().to_list()
    return last_day
