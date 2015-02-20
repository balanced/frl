from __future__ import unicode_literals

import json

from . import RequestLogger


class ClientRequestLogger(RequestLogger):
    """
    Used for implementing a request logger on the client side (e.g. in a remote
    client for an API) using the requests library.

    Example

    ```python
    logger = frl.client.ClientRequestLogger(
        'logger-name',
        ['card_number', 'password']
    )
    response = requests.get('http://google.com')
    logger.log(response)
    ```
    """

    def get_request(self, response):
        return response.request

    def build_request(self, request):
        request_data = dict()
        request_data['url'] = request.url
        request_data['method'] = request.method
        request_data['headers'] = request.headers.items()
        if request.body:
            payload = json.loads(request.body)
            request_data['payload'] = self._mask_fields(payload)
        return request_data

    def build_response(self, response):
        response_data = dict()
        response_data['status'] = response.status_code
        response_data['headers'] = response.headers.items()

        if not self.exclude_body(response):
            if hasattr(response, 'data'):
                response_data['data'] = response.data
            elif hasattr(response, 'content'):
                response_data['data'] = response.content
        return response_data
