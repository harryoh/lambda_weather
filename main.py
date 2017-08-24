# -*- coding: utf-8 -*-

import json
from urllib import urlencode
from urllib2 import urlopen


weather_url = 'https://query.yahooapis.com/v1/public/yql?'
yql_query = 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="jaeju") and u="c"'
yql_url = '{}{}&format=json'.format(weather_url, urlencode({'q': yql_query}))
result = urlopen(yql_url).read().decode('utf-8')
data = json.loads(result)

print json.dumps(data, indent=4, separators=(',', ': '))
