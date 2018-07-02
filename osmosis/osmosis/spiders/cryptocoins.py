# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
import requests

from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class CryptocoinsSpider(scrapy.Spider):
    name = 'cryptocoins'
    allowed_domains = ['coinmarketcap.com']
    start_urls = ['https://api.coinmarketcap.com/v1/ticker/?limit=0']

    def __init__(self):
        url = 'https://api.fixer.io/latest?base=USD'
        self.json_rates = requests.get(url).json()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                    url,
                    callback=self.parse_bin,
                    errback=self.error_bin
                )

    def parse_bin(self, response):
        try:
            json_coins = json.loads(response.text)
            json_return = {
                'now': datetime.date.today(),
                'rates': self.json_rates,
                'coins': json_coins
            }

            return json_return
        except KeyError as err:
            pass

    def error_bin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
