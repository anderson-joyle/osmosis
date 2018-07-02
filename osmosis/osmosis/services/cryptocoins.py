import requests
import json


class BaseEntity(object):
    entity_name = 'base'

    def __init__(self, resource_url, token, coin_data):
        self.resource_url = resource_url
        self.token = token
        self.coin_data = coin_data

    def push(self):
        if not self.exists():
            url = self._get_entity_url()
            headers = self._get_request_header()
            body = self._get_post_body()

            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(body)
            )
            json_response = response.json()

    def fetch(self):
        url = self._get_entity_url()
        url += self._get_url_filtering()
        headers = self._get_request_header()

        json_response = requests.get(url, headers=headers).json()

        return json_response['value']

    def exists(self):
        ret = False
        if len(self.fetch()) > 0:
            ret = True

        return ret

    def _get_entity_url(self):
        return '{0}/data/{1}'.format(self.resource_url, self.entity_name)

    def _get_request_header(self):
        headers = {
            'Authorization': '{0} {1}'.format('Bearer', self.token),
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
        }

        return headers

    def _get_url_filtering(self):
        raise NotImplementedError(
            Class {0} does not implement "_get_url_filtering" method.'.format(
                self.__class__.__name__))

    def _get_post_body(self):
        raise NotImplementedError(
            'Class {0} does not implement "_get_post_body" method.'.format(
                self.__class__.__name__))


class CurrencyISOCodesEntity(BaseEntity):
    entity_name = 'CurrencyISOCodes'

    def _get_url_filtering(self):
        return "?$filter=ISOCurrencyName eq '{0}'".format(self.coin_data['id'])

    def _get_post_body(self):
        body = {
            "ISOCurrencyCode": self.coin_data['symbol'],
            "ISOCurrencyName": self.coin_data['name'],
            "ISOCurrencyCodeNum": '0'
        }

        return body


class CurrenciesEntity(BaseEntity):
    entity_name = 'Currencies'

    def _get_url_filtering(self):
        return "?$filter=Name eq '{0}'".format(self.coin_data['name'])

    def _get_post_body(self):
        body = {
            "CurrencyCode": self.coin_data['symbol'],
            "Name": self.coin_data['name'],
            "Symbol": self.coin_data['symbol'],
            "CurrencyGender": "Male"
        }

        return body


class ExchangeRatesEntity(BaseEntity):
    entity_name = 'ExchangeRates'
