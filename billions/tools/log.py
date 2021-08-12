def log(txt):
    file = r'log.txt'
    with open(file, 'a+') as f:
        f.write(txt+'\n')  # 加\n换行显示

def start():
    file = r'log.txt'
    with open(file, 'a+') as f:
        f.write('The backtest begins'+'\n')  # 加\n换行显示
