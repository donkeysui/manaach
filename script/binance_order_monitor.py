import ccxt
import sys
import json
from influxdb import InfluxDBClient
import time


if __name__ == "__main__":

    # load config
    if len(sys.argv) == 1:
        # default
        config_file = "config/bn_config.json"
    else:
        config_file = sys.argv[1]

    with open(config_file, "r") as file:
        config_file = json.load(file)

    ak = config_file['ak']
    sk = config_file['sk']
    # init 

    binance_client = ccxt.binanceusdm({
            "apiKey": ak,
            "secret": sk,
        })
    influx_client = InfluxDBClient(database="binance")

    # get all position

    for i in range(30):
        balance = binance_client.fetch_balance()
        usdt = balance['total']['USDT']
        busd = balance['total']['BUSD']

    # get all orders
        pass

    # upload
    
        usdt_json = {
            "measurement": "balance_usdt",
            "tags": {
                "instrument_id": "usdt"
            },
            "fields": {
                "usdt": usdt + busd
            }
        }

        influx_client.write_points([usdt_json])
        time.sleep(10)
