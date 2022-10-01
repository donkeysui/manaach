import ccxt
import sys
import json
from influxdb import InfluxDBClient
import time
import datetime

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
    # ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    

    binance_client = ccxt.binanceusdm({
            "apiKey": ak,
            "secret": sk,
        })
    influx_client = InfluxDBClient(database="binance")

    # get all position

    for i in range(30):

        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        balance = binance_client.fetch_balance()
        usdt = balance['total']['USDT']
        busd = balance['total']['BUSD']
        
        positions = config_file['symbols']
        positions = binance_client.fetch_account_positions(positions)
        position_json = {
                "measurement": "binance_position",
                "tags": {
                    "instrument_id": 0
                    },
                "fields": {},
                "time": ts
                }
        try:
            last_position = list(influx_client.query("select last(*) from binance_position"))[0][0]
        except:
            last_position = {}

        for position in positions:
            last_position_value = last_position.get(f"last_{position['symbol']}", 0)
            if not last_position_value:
                last_position_value = 0
            if float(position['info']['positionAmt']) != float(last_position_value):
                # print(position['symbol'], position['info']['positionAmt'], last_position[f"last_{position['symbol']}"])
                position_json['fields'][position['symbol']] = float(position['info']['positionAmt'])

    # get all orders
        

    # upload
    
        usdt_json = {
            "measurement": "balance_usdt",
            "tags": {
                "instrument_id": "usdt"
            },
            "fields": {
                "usdt": usdt + busd
            },
            "time": ts
        }

        points = [usdt_json]
        if position_json['fields']:
            points.append(position_json)

        influx_client.write_points(points)
        time.sleep(10)
