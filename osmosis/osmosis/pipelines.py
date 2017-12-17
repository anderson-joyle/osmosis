# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import json

from azure.storage import CloudStorageAccount
from azure.storage.blob import BlockBlobService


class BasePipeline(object):
    def __init__(self, storage_account, storage_key, storage_connection_string):
        self.blockblob_service = BlockBlobService(storage_account, storage_key)
        self.subscribers = []

    def open_spider(self, spider):
        blob_list = self.blockblob_service.list_blobs(container_name=spider.name, prefix=self._get_subscriber_folder())

        for blob in blob_list:

            blob_text = self.blockblob_service.get_blob_to_text(container_name=spider.name, blob_name=blob.name)
            blob_json = json.loads(blob_text.content)
            self.subscribers.append(
                {'blob_name': blob.name, 'content': blob_json}
            )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            storage_account=crawler.settings.get('AZURE_STORAGE_ACCOUNT_NAME'),
            storage_key=crawler.settings.get('AZURE_STORAGE_KEY'),
            storage_connection_string=crawler.settings.get('AZURE_STORAGE_CONNECTION_STRING')
        )

    def _get_subscriber_folder(self):
        class_name = self.__class__.__name__
        return 'subscribers/{0}'.format(class_name.lower())


class D365AXODataPipeline(BasePipeline):
    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        try:
            for subscriber in self.subscribers:

                try:
                    content = subscriber['content']

                    resource_url = ''
                    token_url = ''

                    if content['version'] == '0.1':
                        channel = content['channel']
                        resource_url = channel['resource']
                        token_url = channel['token_url']

                        body = {
                            'resource': resource_url,
                            'grant_type': channel['grant_type'],
                            'client_secret': channel['client_secret'],
                            'client_id': channel['client_id']
                        }
                    else:
                        raise NotImplementedError('Pipeline {0} does not implement version {1}'.format(self.__class__.__name__, content['version']))

                    response = requests.post(token_url, data=body)
                    response.raise_for_status()

                    json_response = response.json()

                    token = json_response['access_token']
                    token_type = json_response['token_type']

                    subscribed_coins = [x for x in item['coins'] if x['id'] in content['coins']]

                    for coin in subscribed_coins:
                        from osmosis.services.cryptocoins import CurrencyISOCodesEntity, CurrenciesEntity, ExchangeRatesEntity

                        currencyISOCodes = CurrencyISOCodesEntity(resource_url, token, coin)
                        currenciesEntity = CurrenciesEntity(resource_url, token, coin)
                        exchangeRatesEntity = ExchangeRatesEntity(resource_url, token, coin)

                        currencyISOCodes.push()
                        currenciesEntity.push()
                        exchangeRatesEntity.push()
                except NotImplementedError as err:
                    pass
        except KeyError as err:
            pass
        finally:
            return item
        return item


class D365CRMODataPipeline(object):
    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item

# class D365NAVPipeline(object):
#     pass

# class SAPEPipeline(object):
#     pass
