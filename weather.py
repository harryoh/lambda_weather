from __future__ import print_function
from urllib import urlencode
from urllib2 import urlopen

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event=None, context=None):
    weather_url = 'https://query.yahooapis.com/v1/public/yql?'
    yql_query = 'select * from weather.forecast where woeid ' \
                'in (select woeid from geo.places(1) where '\
                'text="{}") and u="c"'.format(event['params']['area'])
    yql_url = '{}{}&format=json'.format(weather_url,
                                        urlencode({'q': yql_query}))
    result = urlopen(yql_url).read().decode('utf-8')
    return json.loads(result)
