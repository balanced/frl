# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

import json
import unittest

import flask
import mock
import requests
from werkzeug.test import Client
from werkzeug.wrappers import Response

import frl
import frl.client
import frl.server


class FlaskApp(flask.Flask):

    def __init__(self, name, request_logger=None):
        super(FlaskApp, self).__init__(name)
        if request_logger:
            self.request_logger = request_logger
            self.after_request(self.log_request)

    def log_request(self, response):
        self.request_logger.log(response)
        return response


def hello_world():
    return 'Hello 漢語!'


class BaseTestCase(unittest.TestCase):
    pass


class ClientTestCase(BaseTestCase):

    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.logger = frl.client.ClientRequestLogger(
            'client-logger', ['card_number'])

    def test_plain_get(self):
        response = requests.get('https://google.com')
        with mock.patch.object(self.logger, 'logger') as logger:
            self.logger.log(response, encode=False)
        self.assertTrue(logger.info.called)
        args, _ = logger.info.call_args
        payload = args[0]
        self.assertItemsEqual(
            payload.keys(),
            ['meta', 'request', 'response']
        )

    def test_mask_fields_json_post(self):
        data = {'card_number': '41111'}
        response = requests.post('https://google.com', json=data)
        with mock.patch.object(self.logger, 'logger') as logger:
            self.logger.log(response, encode=False)
        args, _ = logger.info.call_args
        payload = args[0]
        self.assertDictEqual(
            payload['request']['payload'],
            {"card_number": "XXXXXXXX"}
        )


class ServerTestCase(BaseTestCase):

    def setUp(self):
        super(ServerTestCase, self).setUp()

        self.logger = frl.server.ServerRequestLogger(
            'server-logger', ['card_number'])
        self.app = FlaskApp(__name__, self.logger)
        self.app.route('/', methods=['POST', 'GET'])(hello_world)
        ctx = self.app.test_request_context()
        ctx.push()
        self.addCleanup(ctx.pop)
        self.client = Client(self.app, response_wrapper=Response)

    def test_plain_get(self):
        with mock.patch.object(self.logger, 'logger') as logger:
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logger.info.called)

    def test_mask_fields_form_post(self):
        data = {'card_number': '41111'}
        with mock.patch.object(self.logger, 'logger') as logger:
            self.client.post('/', data=data)
        args, _ = logger.info.call_args
        payload = args[0]
        self.assertIn('"payload": {"card_number": "XXXXXXXX"}', payload)

    def test_mask_fields_json_post(self):
        data = json.dumps({'card_number': '41111'})
        with mock.patch.object(self.logger, 'logger') as logger:
            self.client.post('/', data=data, content_type='application/json')
        args, _ = logger.info.call_args
        payload = args[0]
        self.assertIn('"payload": {"card_number": "XXXXXXXX"}', payload)

    def test_additional_meta_loggers(self):
        def meta_logger(_):
            return {'foo': 'bar'}

        self.logger.meta_population_methods.append(meta_logger)
        with mock.patch.object(self.logger, 'logger') as logger:
            self.client.get('/')
        args, _ = logger.info.call_args
        payload = args[0]
        self.assertIn('"meta": {"foo": "bar"}', payload)

    def test_unicode_payloads(self):
        data = {
            '汉语': '漢語'
        }
        with mock.patch.object(self.logger, 'logger') as logger:
            self.client.post('/', data=data, content_type='application/json')
            self.client.post('/語')
        self.assertEqual(logger.info.call_count, 2)
