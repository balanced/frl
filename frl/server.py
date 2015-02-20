from __future__ import unicode_literals

import json

from . import RequestLogger

from flask import request as current_request


class ServerRequestLogger(RequestLogger):
    """
    Used for implementing a request logger on the client side (e.g. in a remote
    client for an API) using the requests library.

    Example

    ```python
    class FlaskApp(flask.Flask):
        def log_it(self, response):
            logger.log(response)
            return response

    logger = frl.server.ServerRequestLogger(
        'logger-name',
        ['card_number', 'password']
    )

    app = FlaskApp(__name__)
    app.after_request(app.log_it)

    ```
    """

    def __init__(
        self,
        logger_name,
        masked_fields,
        mask='X',
        no_response_body=None,
    ):
        super(ServerRequestLogger, self).__init__(
            logger_name, masked_fields, mask=mask
        )

        # By default, don't log response body for all 2XX
        # responses. no_response_body can be a mixed list of either status
        # codes or tuples of the form ('METHOD', status_code).
        if no_response_body is None:
            no_response_body = range(200, 300)
        self.no_response_body = set()
        for response_code in no_response_body:
            if isinstance(response_code, (int, str)):
                self.no_response_body.add(str(response_code))
            elif isinstance(response_code, tuple):
                self.no_response_body.add(tuple(str(p) for p in response_code))
            else:
                raise TypeError('no_response_body must be a list of ints, '
                                'strs, or tuples')

    def exclude_body(self, response):
        status = response.status
        method = self.get_request(response).method

        # Status is something like '200 OK'
        status_code = status.split()[0]
        method_and_status = (method, status_code)

        return (status_code not in self.no_response_body and
                method_and_status not in self.no_response_body)

    def get_request(self, response):
        return current_request

    def build_request(self, request):
        request_data = dict()
        request_data['url'] = request.url
        request_data['method'] = request.method
        payload = None
        if request.data:
            data = json.loads(request.data)
            payload = self._mask_fields(data)
        elif request.form:
            payload = self._mask_fields(request.form)
        request_data['payload'] = payload

        request_data['headers'] = request.headers.to_list(
            charset='utf-8'
        )
        return request_data

    def build_response(self, response):
        response_data = dict()
        response_data['status'] = response.status
        response_data['headers'] = response.headers.to_list(charset='utf-8')

        if not self.exclude_body(response):
            body = response.response
            if (isinstance(body, list)
                and all(isinstance(x, basestring) for x in body)
            ):
                response_data['data'] = ''.join(c.decode('utf8') for c in body)
        return response_data
