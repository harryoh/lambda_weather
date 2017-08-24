**Create Role**

```
$ aws iam create-role --role-name weather-role \
--assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": { "Service": "lambda.amazonaws.com" },
        "Action": "sts:AssumeRole"
    }]
}'

# output
{
    "Role": {
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    }
                }
            ]
        },
        "RoleId": "AROAJ5EOP7LX3EQY3TTCM",
        "CreateDate": "2017-02-16T11:47:54.089Z",
        "RoleName": "weather-role",
        "Path": "/",
        "Arn": "arn:aws:iam::550931752661:role/weather-role"
    }
}
```

**Attach role**

```
$ aws iam attach-role-policy \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --role-name weather-role
```


## Create Lambda Function

**Install emulambda**

```
$ git clone https://github.com/fugue/emulambda/
$ pip install emulambda
```

**weather.py**

```
from __future__ import print_function
from urllib import urlencode
from urllib2 import urlopen

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event=None, context=None):
    weather_url = 'https://query.yahooapis.com/v1/public/yql?'
    yql_query = 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="{}") and u="c"'.format(event.get('area'))
    yql_url = '{}{}&format=json'.format(weather_url, urlencode({'q': yql_query}))
    result = urlopen(yql_url).read().decode('utf-8')
    return json.loads(result)
```

**api_event.json**

```
{
    "area": "jaeju"
}
```

**Test lambda**

```
$ emulambda -v weather.lambda_handler api_event.json

# output
Executed weather.lambda_handler
Estimated...
...execution clock time:		 1668ms (1700ms billing bucket)
...execution peak RSS memory:		 2M (2711552 bytes)
----------------------RESULT----------------------
{u'query': {u'count': 1, u'lang': u'en-US', u'result...
```

**packaging lambda**

```
$ zip weather_lambda.zip weather.py
```

**Create Lambda Function**

```
$ aws lambda create-function \
  --region ap-northeast-2 \
  --runtime python2.7 \
  --role arn:aws:iam::550931752661:role/weather-role \
  --descript 'get weather' \
  --timeout 10 \
  --memory-size 128 \
  --handler weather.lambda_handler \
  --zip-file fileb://weather_lambda.zip  \
  --function-name GetWeatherOfArea

# output
{
    "CodeSha256": "0bJINrzi1CtBQvHXaSi6wIfuz+Fh+kVlPGK6TA7fTVY=",
    "FunctionName": "GetWeatherOfArea",
    "CodeSize": 516,
    "MemorySize": 128,
    "FunctionArn": "arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea",
    "Version": "$LATEST",
    "Role": "arn:aws:iam::550931752661:role/weather-role",
    "Timeout": 10,
    "LastModified": "2017-02-16T13:46:30.781+0000",
    "Handler": "weather.lambda_handler",
    "Runtime": "python2.7",
    "Description": "get weather"
}
```

**Update Lambda Function**

```
$ aws lambda update-function-code \
  --function-name GetWeatherOfArea \
  --zip-file fileb://weather_lambda.zip

# output
{
    "CodeSha256": "0bJINrzi1CtBQvHXaSi6wIfuz+Fh+kVlPGK6TA7fTVY=",
    "FunctionName": "GetWeatherOfArea",
    "CodeSize": 516,
    "MemorySize": 128,
    "FunctionArn": "arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea",
    "Version": "$LATEST",
    "Role": "arn:aws:iam::550931752661:role/weather-role",
    "Timeout": 10,
    "LastModified": "2017-02-16T13:48:07.148+0000",
    "Handler": "weather.lambda_handler",
    "Runtime": "python2.7",
    "Description": "get weather"
}
```

## API Gateway

**create api**

```
$ aws apigateway create-rest-api  \
  --region ap-northeast-2 \
  --name 'Weather API' \
  --description 'Show weather of requested area'

# output
{
    "id": "8ma5wc7ye9",
    "name": "Weather API",
    "description": "Show weather of requested area",
    "createdDate": 1487352113
}
```

**Get / reousrce id**

```
$ aws apigateway get-resources  \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9

# output
{
    "items": [
        {
            "path": "/",
            "id": "mdcteg2fd0"
        }
    ]
}
```

**Create /api resource**

```
$ aws apigateway create-resource  \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --parent-id mdcteg2fd0 \
  --path-part api

# output
{
    "path": "/api",
    "pathPart": "api",
    "id": "2khdrl",
    "parentId": "mdcteg2fd0"
}
```

**Create /api/v1 resource**

```
$ aws apigateway create-resource  \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --parent-id 2khdrl \
  --path-part v1

# output
{
    "path": "/api/v1",
    "pathPart": "v1",
    "id": "y4dl65",
    "parentId": "2khdrl"
}
```

**Create /api/v1/weather resource**

```
$ aws apigateway create-resource \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --parent-id y4dl65 \
  --path-part weather

# output
{
    "path": "/api/v1/weather",
    "pathPart": "weather",
    "id": "6oc3qu",
    "parentId": "y4dl65"
}
```

**Create /api/v1/weather/{area} resource**

```
$ aws apigateway create-resource \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --parent-id 6oc3qu \
  --path-part {area}

# output
{
    "path": "/api/v1/weather/{area}",
    "pathPart": "{area}",
    "id": "r5p13j",
    "parentId": "6oc3qu"
}
```

**Create Get Method**

```
$ aws apigateway put-method  \
  --rest-api-id 8ma5wc7ye9 \
  --resource-id r5p13j \
  --http-method GET \
  --authorization-type NONE

# output
{
    "apiKeyRequired": false,
    "httpMethod": "GET",
    "authorizationType": "NONE"
}
```


**intration with lambda**

```
$ aws apigateway put-integration \
  --rest-api-id 8ma5wc7ye9 \
  --resource-id r5p13j \
  --http-method GET \
  --type AWS \
  --integration-http-method GET \
  --uri 'arn:aws:apigateway:ap-northeast-2:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea/invocations'
  
# output
{
    "httpMethod": "GET",
    "passthroughBehavior": "WHEN_NO_MATCH",
    "cacheKeyParameters": [],
    "type": "AWS",
    "uri": "arn:aws:apigateway:ap-northeast-2:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea/invocations",
    "cacheNamespace": "r5p13j"
}

```

**Set Response**

```
$ aws apigateway put-method-response \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --resource-id r5p13j \
  --http-method GET \
  --status-code 200 \
  --response-models "{\"application/json\": \"Empty\"}"

# output
{
    "responseModels": {
        "application/json": "Empty"
    },
    "statusCode": "200"
}

$ aws apigateway put-integration-response \
  --region ap-northeast-2 \
  --rest-api-id 8ma5wc7ye9 \
  --resource-id r5p13j \
  --http-method GET \
  --status-code 200 \
  --response-templates "{\"application/json\": \"\"}"

# output
{
    "statusCode": "200",
    "responseTemplates": {
        "application/json": null
    }
}
```

**Deploy API**

```
$ aws apigateway create-deployment \
  --rest-api-id 8ma5wc7ye9 \
  --stage-name prod

# output
{
    "id": "ccfzbg",
    "createdDate": 1487358560
}
```

**Set Permission**

```
$ aws lambda add-permission \
  --region ap-northeast-2 \
  --function-name GetWeatherOfArea \
  --statement-id weather-test-api-3 \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-northeast-2:550931752661:8ma5wc7ye9/*/GET/api/v1/weather/*"

# output
{
    "Statement": "{\"Sid\":\"weather-test-api-1\",\"Resource\":\"arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"apigateway.amazonaws.com\"},\"Action\":[\"lambda:InvokeFunction\"],\"Condition\":{\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:execute-api:ap-northeast-2:550931752661:8ma5wc7ye9/*/GET/api/v1/weather/*\"}}}"
}

$ aws lambda add-permission \
  --function-name GetWeatherOfArea \
  --statement-id weather-prod-api-3 \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-northeast-2:550931752661:8ma5wc7ye9/prod/GET/api/v1/weather/*"

#output
{
    "Statement": "{\"Sid\":\"weather-prod-api-1\",\"Resource\":\"arn:aws:lambda:ap-northeast-2:550931752661:function:GetWeatherOfArea\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"apigateway.amazonaws.com\"},\"Action\":[\"lambda:InvokeFunction\"],\"Condition\":{\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:execute-api:ap-northeast-2:550931752661:8ma5wc7ye9/prod/GET/api/v1/weather/*\"}}}"
}
```


**Test Invoke**

```
$ aws apigateway test-invoke-method \
  --rest-api-id 8ma5wc7ye9 \
  --resource-id r5p13j \
  --http-method GET
```
