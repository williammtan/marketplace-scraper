import re
from graphql.parser import GraphQLParser
from scrapy.utils.project import get_project_settings
import scrapy
import json
import numpy as np


class BaseSpiderGQL(object):
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'scrapyfood.middlewares.TokpedGQLSpiderMiddleware': 543,
        }
    }

    def parse_split(self, response, args=None, **kwargs):
        data = response.json()
        if args == None:
            yield from self.parse(data['data'], **kwargs)
        else:
            for i in range(len(data)):
                yield from self.parse(data[i]['data'], **args[i])


class TokpedGQL():
    operation_name = 'example_operation_name'
    query = 'example_query_name'
    url = 'https://gql.tokopedia.com/'
    request_cue = []
    request_cue_length = 100

    def __init__(self, operation_name, query, default_variables={}):
        request_cue_length = get_project_settings()['REQUEST_CUE']
        self.operation_name = operation_name
        self.query = query
        self.default_variables = default_variables
        self.request_cue_length = request_cue_length
        self.parser = GraphQLParser()

    def verify(self, variables):
        ast = self.parser.parse(self.query)
        variable_definitions = ast.definitions[0].variable_definitions
        for var in variable_definitions:
            if var.name not in variables.keys():
                raise Exception(f'Variable {var.name} not filled in query!')

    def convert(self, o):
        if isinstance(o, np.int64):
            return int(o)
        raise TypeError

    def parse_split(self, response, cb_kwargs, callbacks):
        data = response.json()
        for i in range(len(data)):
            callbacks(data[i], **cb_kwargs[i])

    def request(self, callback, cb_kwargs=None, **kwargs):
        input_variables = kwargs
        # overide default vars
        vars = self.default_variables
        for k, v in input_variables.items():
            vars[k] = v

        self.verify(vars)
        body = {
            'operationName': self.operation_name,
            'variables': vars,
            'query': self.query
        }

        self.request_cue.append({
            'body': body,
            'cb_kwargs': cb_kwargs
        })

        if len(self.request_cue) == self.request_cue_length:
            json_body = json.dumps(
                [req['body'] for req in self.request_cue], default=self.convert)
            yield scrapy.Request(url=self.url, method='POST', body=json_body, headers={
                'Content-Type': 'application/json', 'referer': 'aaa'
            }, callback=self.parse_split, cb_kwargs={'cb_kwargs': [req['cb_kwargs'] for req in self.request_cue], 'callbacks': callback})

        # return scrapy.Request(url=self.url, method='POST', body=body, headers={'Content-Type': 'application/json', 'referer': 'https://www.tokopedia.com/asahealthyshop/1-kg-organic-chia-seed-mexico?src=topads'}, callback=callback, cb_kwargs=cb_kwargs)

    def request_old(self, callback, cb_kwargs=None, **kwargs):
        input_variables = kwargs
        # overide default vars
        vars = self.default_variables
        for k, v in input_variables.items():
            vars[k] = v

        # self.verify(vars)
        body = {
            'operationName': self.operation_name,
            'variables': vars,
            'query': self.query
        }
        json_body = json.dumps(body)

        return scrapy.Request(url=self.url, method='POST', body=json_body, headers={'Content-Type': 'application/json', 'referer': 'aaaa'}, callback=callback, cb_kwargs=cb_kwargs)
