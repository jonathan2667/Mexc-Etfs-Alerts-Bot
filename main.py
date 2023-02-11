from mexc_sdk_1.src.mexc_sdk import Spot
import time
import requests
import json
from datetime import datetime
from datetime import timedelta
import time
import telebot
from numerize import numerize


cnt = 0
ind = 0
symb = []
hour = 0

dict_cont = {
}

def write_symb(cnt):
    with open(r"C:\Users\jmogo\PycharmProjects\mexc1\5xetfsraw.txt", 'r') as f:
        datafile = f.readlines()
    for line in datafile:
        if 'symbol_name__1vTU4' in line:
            start = line.find('4">') + 3
            end = line.find('</div>') - 2
            cnt += 1
            symb.append(line[start:end])
    print(cnt)
    cnt = 0
    with open('symbols5xETFS.txt', 'w') as f:
        for line in symb:
            cnt += 1
            if (cnt % 2 == 0) :
                f.write(line)
                f.write('\n')

def write_cont() :
    counter = 0
    with open(r"C:\Users\jmogo\PycharmProjects\mexc1\ContFile.txt", 'r') as f:
        datafile = f.readlines()
    for i, line in enumerate(datafile):
        if 'Cont' in line:
            end =  line.find('</td>') - 8
            symbol = datafile[i + 3][0:end]
            cont = float(datafile[i + 2])
            dict_cont[symbol] = cont

def get_ts_rebalancing() :
    now = datetime.now()
    time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0)
    if (now.hour < 18):
        time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0) - timedelta(days = 1)

    ts = datetime.timestamp(time_rebalance)

    return int(ts)

def get_current_price(symbol_name) :
    r = requests.get("https://contract.mexc.com/api/v1/contract/fair_price/" + symbol_name + "_USDT")
    json_r = r.json()

    return json_r['data']['fairPrice']


def get_rebalancing_price(symbol_name):
    r = requests.get(
        "https://contract.mexc.com/api/v1/contract/kline/" + symbol_name + "_USDT?interval=Min1&start=" + str(
            get_ts_rebalancing()) + "&end=" + str(get_ts_rebalancing()))

    json_r = r.json()

    return json_r['data']['open'][0]

def get_high_price(symbol_name) :
    now = datetime.now() - timedelta(minutes=2)

    ts_now = int(datetime.timestamp(now))

    time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0)
    if (now.hour < 18):
        time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0) - timedelta(days = 1)
    ts_rebl = int(datetime.timestamp(time_rebalance))

    r = requests.get("https://contract.mexc.com/api/v1/contract/kline/" + symbol_name + "_USDT?interval=Min1&start=" + str(ts_rebl) + "&end=" + str(ts_now))

    json_r = r.json()

    return max(json_r['data']['high'])

def get_min_price(symbol_name) :
    now = datetime.now() - timedelta(minutes=2)
    ts_now = int(datetime.timestamp(now))

    time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0)
    if (now.hour < 18):
        time_rebalance = datetime(now.year, now.month, now.day, 18, 0, 0) - timedelta(days = 1)
    ts_rebl = int(datetime.timestamp(time_rebalance))

    r = requests.get("https://contract.mexc.com/api/v1/contract/kline/" + symbol_name + "_USDT?interval=Min1&start=" + str(ts_rebl) + "&end=" + str(ts_now))

    json_r = r.json()

    return min(json_r['data']['low'])

def get_volume_futures_USDT(symbol_name) :
    r = requests.get("https://contract.mexc.com/api/v1/contract/ticker?symbol=" +  symbol_name + "_USDT")
    json_r = r.json()

    return round((int(float(json_r['data']['volume24']))) * dict_cont[symbol_name]   * 1.00 * float(json_r['data']['lastPrice']) , 2)

def get_volume_etf_USDT(symbol_name) : #3s !!!
    r = requests.get("https://api.mexc.com/api/v3/ticker/24hr?symbol=" + symbol_name + "USDT")
    json_r = r.json()

    return round((int(float(json_r['volume'])))   * 1.00 * float(json_r['lastPrice']), 2)

def market_impact(etf_volume, futures_volume):
    ratio = etf_volume * 1.00 / float(futures_volume)

    if (ratio >= 10): return '🔴🔴🔴🔴🔴'
    if (ratio >= 5): return '🔴🔴🔴'
    if (ratio >= 1): return '🔴🔴'
    return '🔴'

def test():
    print(get_rebalancing_price('ZEN'))



#client = Spot(api_key='mx0vglsbkmjf1APg0v', api_secret='d8d0ea57436446578c642127aaaf963b')




API_KEY = '5419960375:AAGMY3WE_RCaSt8Z4UghgQ026CUqlT2hWVQ'
#chat_id = '5503700037'
chat_id = '-612169610'

bot = telebot.TeleBot(API_KEY)


write_cont()



while(1):
    now = datetime.now()
    
    if (now.hour != hour):
        bot.send_message(chat_id, str(now))
        hour = now.hour

    with open(r"C:\Users\jmogo\PycharmProjects\mexc1\symbols3xETFS.txt", 'r') as f:
        datafile = f.readlines()

    for line in datafile:
        try :
            line = line[0:len(line) - 1]

            rebal_price = get_rebalancing_price(line)
            curr_price = get_current_price(line)

            high_price = get_high_price(line)
            min_price = get_min_price(line)

            percentage_increase = round(((curr_price - rebal_price) * 1.00 / rebal_price) * 100.00, 2) #curr 50 reb 45
            percentage_decrease = round(((rebal_price - curr_price) * 1.00 / rebal_price) * 100.00, 2) #curr 45 reb 50

            # long 3x
            if (curr_price > rebal_price):
                if (percentage_increase > 9):
                    txt = line + " percentage: " + str(percentage_increase) + "% reb "  +  str(rebal_price) + " curr " + str(curr_price)
                    print(txt)
                    if (high_price < curr_price and curr_price < 1.18 * rebal_price):
                        etf_volume = get_volume_etf_USDT(line + '3S')
                        futures_volume = get_volume_futures_USDT(line)
                        text2 = line + " 3X CLOSE TO REBALANCING UP: \n" + \
                                "Percentage: " + str(percentage_decrease) + \
                                "% \nRebalance Price: " + str(rebal_price) + \
                                " \nCurrent Price: " + str(curr_price) + \
                                "\nVolume USDT of ETF 3S: " + numerize.numerize(etf_volume) + \
                                "\nVolume USDT of FUTURES: " + numerize.numerize(futures_volume) + \
                                '\nMarket impact:' + market_impact(etf_volume, futures_volume)

                        bot.send_message(chat_id, text2)

                if (percentage_increase > 25) :
                    txt = line + " percentage: " + str(percentage_increase) + "% reb "  +  str(rebal_price) + " curr " + str(curr_price)
                    print(txt)
                    if (high_price < curr_price and curr_price < 1.33 * rebal_price):
                        etf_volume = get_volume_etf_USDT(line + '3S')
                        futures_volume = get_volume_futures_USDT(line)
                        text2 = line + " 3X CLOSE TO REBALANCING UP: \n" + \
                                "Percentage: " + str(percentage_decrease) + \
                                "% \nRebalance Price: " + str(rebal_price) + \
                                " \nCurrent Price: " + str(curr_price) + \
                                "\nVolume USDT of ETF 3S: " + numerize.numerize(etf_volume) + \
                                "\nVolume USDT of FUTURES: " + numerize.numerize(futures_volume) + \
                                '\nMarket impact:' + market_impact(etf_volume, futures_volume)

                        bot.send_message(chat_id, text2)

            #short 3x

            if (curr_price < rebal_price):
                if (percentage_decrease > 10):
                    txt = line + " percentage: " + str(percentage_decrease ) + "% reb "  +  str(rebal_price) + " curr" + str(curr_price)

                    print(txt)
                    if (min_price > curr_price and curr_price > 0.82 * rebal_price):
                        etf_volume = get_volume_etf_USDT(line + '3L')
                        futures_volume = get_volume_futures_USDT(line)
                        text2 = line + " 3X CLOSE TO REBALANCING DOWN: \n" + \
                                "Percentage: " + str(percentage_decrease) + \
                                "% \nRebalance Price: " + str(rebal_price) + \
                                " \nCurrent Price: " + str(curr_price) + \
                                "\nVolume USDT of ETF 3L: " + numerize.numerize(etf_volume) + \
                                "\nVolume USDT of FUTURES: " + numerize.numerize(futures_volume) +\
                                '\nMarket impact:' + market_impact(etf_volume, futures_volume)

                        bot.send_message(chat_id,  text2)

                if (percentage_decrease > 23):
                    txt = line + " percentage: " + str(percentage_decrease ) + "% reb"  +  str(rebal_price) + " curr" + str(curr_price)
                    print(txt)
                    if (min_price > curr_price and curr_price > 0.69 * rebal_price):
                        etf_volume = get_volume_etf_USDT(line + '3L')
                        futures_volume = get_volume_futures_USDT(line)
                        text2 = line + " 3X CLOSE TO REBALANCING DOWN: \n" + \
                                "Percentage: " + str(percentage_decrease) + \
                                "% \nRebalance Price: " + str(rebal_price) + \
                                " \nCurrent Price: " + str(curr_price) + \
                                "\nVolume USDT of ETF 3L: " + numerize.numerize(etf_volume) + \
                                "\nVolume USDT of FUTURES: " + numerize.numerize(futures_volume) + \
                                '\nMarket impact:' + market_impact(etf_volume, futures_volume)

                        bot.send_message(chat_id, text2)


        except (KeyError, IndexError) as e:
            print(line + " " + str(e))

    # with open(r"C:\Users\jmogo\PycharmProjects\mexc1\symbols5xETFS.txt", 'r') as f:
    #     datafile = f.readlines()
    #
    # for line in datafile:
    #     try :
    #         line = line[0:len(line) - 1]
    #
    #         rebal_price = get_rebalancing_price(line)
    #         curr_price = get_current_price(line)
    #
    #         high_price = get_high_price(line)
    #         min_price =  get_min_price(line)
    #
    #         four_percent_up = 1.04 * rebal_price
    #         eleven_percent_up = 1.11 * rebal_price #1.1449
    #
    #         four_percent_down = 0.96 * rebal_price
    #         eleven_percent_up = 0.90 * rebal_price # 0.8742
    #
    #         # long 5x
    #         if (curr_price > four_percent_up):
    #             percentage_increase = ((curr_price - rebal_price) * 1.00 / rebal_price)
    #             txt = line + " percentage: " + str(round(percentage_increase * 100.00, 2)) + "%"
    #             print(txt)
    #             if (high_price < curr_price and high_price < 1.1 * rebal_price):
    #                 bot.send_message(chat_id, "5X CLOSE TO REBALANCING UP: " + txt)
    #
    #         if (curr_price > eleven_percent_up):
    #             percentage_increase = ((curr_price - rebal_price) * 1.00 / rebal_price)
    #             txt = line + " percentage: " + str(round(percentage_increase * 100.00, 2)) + "%"
    #             print(txt)
    #             if (high_price < curr_price and high_price < 1.17 * rebal_price):
    #                 bot.send_message(chat_id, "5X CLOSE TO REBALANCING UP SECOND TIME: " + txt)
    #
    #         # short 5x
    #
    #         if (curr_price < four_percent_down):
    #             percentage_decrease = ((rebal_price - curr_price) * 1.00 / rebal_price)
    #             txt = line + " percentage: " + str(round(percentage_decrease * 100.00, 2)) + "%"
    #             print(txt)
    #             if (min_price > curr_price and min_price > 0.91 * rebal_price):
    #                 bot.send_message(chat_id, "5X CLOSE TO REBALANCING DOWN: " + txt)
    #
    #         if (curr_price < eleven_percent_up):
    #             percentage_decrease = ((rebal_price - curr_price) * 1.00 / rebal_price)
    #             txt = line + " percentage: " + str(round(percentage_decrease * 100.00, 2)) + "%"
    #             print(txt)
    #             if (min_price > curr_price and min_price > 0.83 * rebal_price):
    #                 bot.send_message(chat_id, "5X CLOSE TO REBALANCING DOWN: " + txt)
    #
    #     except (KeyError, IndexError) as e:
    #         print(line + " " + str(e))


bot.polling()


#do not forget about 3s 3l tokens 2 times