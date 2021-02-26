import pandas as pd


class AlphaVantageRequestor:

    URL = "https://www.alphavantage.co/query?function="

    def __init__(self, api_key):
        self._api_key = api_key

    def getListOfStocks(self):
        return pd.read_csv(self.URL + "LISTING_STATUS&apikey=" + self._api_key)
