def format_gauges_chile2015(gaugeinfo):
    import pandas as pd
    for gaugeno, offset in gaugeinfo:
        df = pd.read_csv('dart{}.txt'.format(gaugeno), delim_whitespace=True)
        df.columns = ['time', 'year', 'month', 'day', 'hours', 'minutes', 'seconds', 'raw_obs', 'fitted_tidal', 'residual', 'blank']
        df = df[['time', 'residual']]
        origin_time = 259 + (22 * 60**2 + 54*60 + 32.860)/(24 * 60**2)
        df.time = df.time.map(lambda time : 24*60**2 * (time-origin_time))
        df.residual = df.residual.map(lambda res : res + offset)
        df.to_csv('{}_notide.txt'.format(gaugeno), index=False, header=False, sep=' ')