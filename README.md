# FRL Flask Requests Logger

[![Build Status](https://secure.travis-ci.org/balanced/frl.png?branch=master)](http://travis-ci.org/balanced/frl) [![Latest Version](https://pypip.in/version/frl/badge.svg)](https://pypi.python.org/pypi/frl/) [![Downloads](https://pypip.in/download/frl/badge.svg)](https://pypi.python.org/pypi/frl/) [![Supported Python versions](https://pypip.in/py_versions/frl/badge.svg)](https://pypi.python.org/pypi/frl/) [![License](https://pypip.in/license/frl/badge.svg)](https://pypi.python.org/pypi/frl/)

A request logger for requests and responses from the requests and flask libraries that logs in a standard format

```json
{
   "meta":{

   },
   "request":{
      "headers":[
         [
            "Host",
            "localhost"
         ],
         [
            "Content-Length",
            "0"
         ],
         [
            "Content-Type",
            ""
         ]
      ],
      "url":"http://localhost/",
      "method":"GET"
   },
   "response":{
      "status":"200 OK",
      "headers":[
         [
            "Content-Type",
            "text/html; charset=utf-8"
         ],
         [
            "Content-Length",
            "12"
         ]
      ],
      "data":"Hello World!"
   }
}
```

## Configure flask


## Configure requests


```python
logger = frl.client.ClientRequestLogger(
    'logger-name',
    ['card_number', 'password']
)
response = requests.get('http://google.com')
logger.log(response)
```

You can mask sensitive data from payloads.


You can add additional data into the meta field.
