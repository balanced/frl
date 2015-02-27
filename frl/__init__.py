from __future__ import unicode_literals

import logging
import json

__version__ = '0.0.3'


class RequestLogger(object):

    encoder = staticmethod(json.dumps)

    meta_population_methods = []

    def __init__(self, logger_name, masked_fields, mask='X'):
        self.logger = logging.getLogger(logger_name)
        self.masked_fields = masked_fields
        self.mask = mask

    def _mask_fields(self, payload):
        if not isinstance(payload, dict):
            return payload
        masked_payload = {}
        for key, value in payload.iteritems():
            if key in self.masked_fields:
                if self.mask is None:
                    continue
                if isinstance(value, basestring):
                    # NOTE: hide masked field length
                    value = self.mask * 8
                else:
                    value = self.mask
            elif isinstance(value, dict):
                value = self._mask_fields(value)
            masked_payload[key] = value
        return masked_payload

    @classmethod
    def exclude_body(cls, response):
        """
        Override if you want to conditionally filter out the body from the
        logged response.
        """
        return False

    @classmethod
    def exclude_request(cls, request):
        """
        Override if you want to conditionally filter out the entire request
        from being logged.
        """
        return False

    @property
    def _empty_entry(self):
        return {
            'request': {
                'url': None,
                'method': None,
                'headers': {},
                'payload': None
            },
            'response': {
                'status': None,
                'headers': {},
                'data': None,
            },
            'meta': {

            }
        }

    def get_request(self, response):
        raise NotImplementedError()

    def build_entry(self, response):
        data = self._empty_entry

        request = self.get_request(response)

        if self.exclude_request(request):
            return

        data['request'].update(self.build_request(request))
        data['response'].update(self.build_response(response))
        data['meta'].update(self.build_meta(response))

        return data

    def build_request(self, request):
        return {}

    def build_response(self, response):
        return {}

    def build_meta(self, response):
        meta_data = dict()
        for populate in self.meta_population_methods:
            meta_data.update(populate(response))
        return meta_data

    def log(self, response, encode=True):
        entry = self.build_entry(response)

        if not entry:
            return

        if encode:
            entry = self.encoder(entry)

        self.logger.info(entry)
