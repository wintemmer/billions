import pandas as pd


def __init__():
    pass


def load(fname, cname, ftype='csv'):
    """
    Read data from file.

    args:
        fname: factor file name (with columns: [factor, trade_dt, code])
        cname: close file name (with columns: [close, trade_dt, code])
        type: file type ([csv, xlsx, json])

    returns:
        data: 2-index(trade_dt, code), factor, close
    """

    # check out filetype
    if ftype == 'csv':
        read = pd.read_csv
    elif ftype == 'xlsx':
        read = pd.read_excel
    elif ftype == 'json':
        read = pd.read_json
    else:
        print('TYPE NOT SUPPORTED! Try other types like:')
        print(['csv', 'xlsx', 'json'])
        return

    # read data
    try:
        factor = read(fname)
        close = read(cname)
    except ValueError:
        print('WRONG TYPE, please check out your file type')
        return

    # choose the right columns
    factor = factor[['trade_dt', 'code', 'factor']]
    close = close[['trade_dt', 'code', 'close']]

    # combine two data set into one
    data = factor.merge(close, how='inner')
    data.trade_dt = pd.DatetimeIndex(data.trade_dt)
    data = data.set_index(['trade_dt', 'code'])

    return data
