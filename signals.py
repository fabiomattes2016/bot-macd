import pandas as pd
import numpy as np


class Signals:
    def __init__(self, df, lags):
        self.df = df
        self.lags = lags

    def get_trigger(self):
        dfx = pd.DataFrame()

        for i in range(self.lags + 1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)

        return dfx.sum(axis=0)

    def decide(self):
        self.df['trigger'] = np.where(self.get_trigger(), 1, 0)
        self.df['Buy'] = np.where(
            (self.df.trigger)
            & (self.df['%K'].between(20, 80))
            & (self.df['%D'].between(20, 80))
            & (self.df.rsi > 50) & (self.df.macd > 0),
            1,
            0
        )
