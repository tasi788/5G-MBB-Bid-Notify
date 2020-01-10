__author__ = '踢低吸'

import json
import time
from dateutil import tz
from datetime import datetime

import logging
import coloredlogs

import requests
import schedule
import telegram
from pyquery import PyQuery as pq

import config


logger = logging.getLogger(__name__)
coloredlogs.install(level=config.log)
timezone = tz.gettz('Asia/Taipei')


class bot:
    def __init__(self):
        self.bot = telegram.Bot(config.token)
        logger.info(self.bot.get_me().first_name)

    def loaddata(self, query: None):
        f = open('data.json', 'r').read()
        load = json.loads(f)

        if query not in load:
            load.append(query)
            with open('data.json', 'w') as f:
                f.write(json.dumps(load, ensure_ascii=False))
            return True
        else:
            return False

    def loadpage_price(self):
        url = f'https://mbb5g.ncc.gov.tw/round_list.html?t={int(time.time())}'
        r = requests.get(url)
        r.encoding = 'utf8'
        logger.info('Load Price')
        if r.status_code != 200:
            logger.critical('load page failed')
            return False

        trim = pq(r.text).text().split('\n')
        for x in range(12, len(trim), 12):
            if x == 12:
                s = 0
            else:
                s = x - 12

            data = trim[s:x]

            if self.loaddata(data[0]):
                pass
            else:
                return

            # total price
            url = 'https://mbb5g.ncc.gov.tw/index01.html'
            r = requests.get(url)
            r.encoding = 'utf8'
            logger.info('Load Total Price')
            if r.status_code != 200:
                logger.critical('load total price failed')
                return False

            total = '-'
            try:
                total = list(pq(r.text)('.content')('.unit').items())[
                    0].text().split('總標金：')[1]
            except Exception as e:
                logger.critical(e)

            text = f'\[{data[0]}]\n\n' + \
                '*1800MHz*\n' + \
                f'回合價：`{data[1]}`\n' + \
                f'暫時得標頻寬：`{data[2]}`\n' + \
                f'暫時得標金：`{data[3]}`\n\n' + \
                '*3500MHz*\n' + \
                f'回合價：`{data[4]}`\n' + \
                f'回合價暫得標頻寬：`{data[5]}`\n' + \
                f'暫時得標頻寬：`{data[6]}`\n' + \
                f'暫時得標金：`{data[7]}`\n\n' + \
                '*28000MHz*\n' + \
                f'回合價：`{data[8]}`\n' + \
                f'回合價暫得標頻寬：`{data[9]}`\n' + \
                f'暫時得標頻寬：`{data[10]}`\n' + \
                f'暫時得標金：`{data[11]}`\n\n' + \
                f'總標金：`{total}`\n' + \
                f'暫時得標金單位：新臺幣百萬元'
            self.bot.send_message(config.channel, text, parse_mode='markdown')

    def loadpage_company(self):
        url = 'https://mbb5g.ncc.gov.tw/index02.html'
        r = requests.get(url)
        r.encoding = 'utf8'
        logger.info('Load Company Num')
        if r.status_code != 200:
            logger.critical('load page failed')
            return False
        try:
            restult = r.text.split("name: '合格競價者家數',")[
                1].split('data: ')[1].split('\r\n')[0]
        except:
            logger.critical('trim error')
            return False

        company = len(eval(result))
        now = datetime.now(timezone).date().strftime('%Y年%m月%d日')
        text = f'今日 {now} 競標結束\n' +\
               f'剩餘合格競標廠商：`{company}`\n\n' +\
            '#競標結束'
        self.bot.send_message(config.channel, text, parse_mode='markdown')


notify = bot()
schedule.every(10).minutes.do(notify.loadpage_price)
schedule.every().day.at('18:01').do(notify.loadpage_company)

while True:
    schedule.run_pending()
    time.sleep(1)
