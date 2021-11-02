# this script explores the gql schema in tokped

from graphql.parser import GraphQLParser
from graphql.ast import Field, Query, NonNullType, Variable
from seleniumwire import webdriver
from scrapyfood.constants import proxy_base as proxy_url
import threading
import argparse
import requests
import time
import json
import os


class GQLExplorer():
    def __init__(self, output_dir, format_gql=False, parse_gql=False):
        self.output_dir = output_dir
        self.format_gql = format_gql
        self.parse_gql = parse_gql

        self.setup_webdriver()
        self.gql_parse = GraphQLParser()

        self.watch_thread = threading.Thread(target=self.watch, name="Watch gql requests")
        self.watch_thread.start()
        self.driver.get('https://tokopedia.com')

    def setup_webdriver(self):
        self.driver = webdriver.Chrome(seleniumwire_options={'port': 12345})
    
    def watch(self):

        time.sleep(0.5) # wait 

        # do stuff
        gql_requests = [req for req in self.driver.requests if req.url == 'https://gql.tokopedia.com/']
        thread_list = []
        for req in gql_requests:
            thread = threading.Thread(target=self.process_gql_request, args=(req, ))
            thread_list.append(thread)

        for thread in thread_list:
            thread.start()
        
        for thread in thread_list:
            thread.join()

        del self.driver.requests # reset requests

        self.watch() # reload
    
    def process_gql_request(self, gql_request):
        body = json.loads(gql_request.body)
        for req_query in body:
            name = req_query['operationName']
            variables = req_query['variables']
            if 'query' not in req_query.keys():
                print('skipping, no param in gql request')
                continue
            gql_query = self.gql_parse.parse(req_query['query']).definitions[0]
            if self.parse_gql:
                self.process_query(name, gql_query)
            else:
                query_dir = os.path.join(self.output_dir, gql_query.name)
                if not os.path.isdir(query_dir):
                    os.makedirs(query_dir)
                f = open(os.path.join(query_dir, 'query.gql'), 'w')
                f.write(req_query['query'])
                f.close()
                if variables != {} or variables is not None:
                    f = open(os.path.join(query_dir, 'variables.json'), 'w')
                    f.write(json.dumps(variables))
    
    def gql_file(self, name, o=False, mode='r'):
        fname = os.path.join(self.output_dir, name + '.gql')
        if o:
            if mode == 'r':
                if not os.path.isfile(fname) or os.stat(fname).st_size == 0:
                    return None
                f = open(fname, mode).read()
            elif mode == 'w':
                f = open(fname, mode)
            return f
        else:
            return fname

    def gql_query_by_name(self, name):
        """Find and get gql query from file (return None if no file exists)"""
        data = self.gql_file(name, o=True)
        if data:
            gql_query = self.gql_parse.parse(data).definitions[0]
            return gql_query
        else:
            return None


    def process_query(self, name, gql_query):
        """Find gql query file and rewrite with new query"""
        host_gql_query = self.gql_query_by_name(name)
        f = self.gql_file(name, o=True, mode='w')
        if host_gql_query == None:
            print(f'Creating {gql_query.name}')
            f.write(self.make_gql_query(gql_query))
        else:
            # ovewrite query
            print(f'Merging {host_gql_query.name}')
            f.write(self.rewrite_query(gql_query_a=host_gql_query, gql_query_b=gql_query))
    
    def has_child(self, field):
        return field.selections != []
    
    def rewrite_query(self, gql_query_a: Query, gql_query_b : Query):
        """Rewrite and merge query"""

        def merge_field(query_a: Field, query_b: Field):
            """Merges 2 fields recursively"""
            for b_field in query_b.selections: # for field in query_b
                a_field = [a for a in query_a.selections if a.name == b_field.name]
                if a_field != []:
                    # b is in a
                    a_field = a_field[0]
                    if self.has_child(a_field) and self.has_child(b_field): # if it has children, merge again
                        query_a.selections = [field for field in query_a.selections if field.name != a_field.name] # delete a_field
                        query_a.selections = query_a.selections + [merge_field(query_a=a_field, query_b=b_field)]
                    elif a_field.name == b_field.name:
                        pass
                else:
                    # b is not in a, just append
                    query_a.selections = query_a.selections + [b_field]
            return query_a  

        merged_query = merge_field(
            query_a=gql_query_a, 
            query_b=gql_query_b
        )
        
        return self.make_gql_query(merged_query)

    def make_gql_query(self, query: Query) -> str:
        """Converts Query object to string"""
        def dumps_field(field: Field):
            out = '{ '
            for f in field.selections:
                if self.has_child(f): # process f
                    out += f.name
                    if f.arguments != []:
                        dollar = '$'
                        out += '(' + ', '.join([f'{var.name}: {dollar + var.value.name if type(var.value) == Variable else var.value}' for var in f.arguments]) + ') '
                    out += ' ' + dumps_field(f)
                else:
                    out += ' ' + f.name
            out += ' } '
            return out
        
        ex = '!'
        blank = ''
        variables = [f'${var.name}: {var.type.name if type(var.type) != NonNullType else var.type.type.name}{ex if type(var.type) == NonNullType else blank}' for var in query.variable_definitions]
        variables_str = '(' + ', '.join(variables) + ') '  if len(variables) != 0 else ''
        raw = 'query ' + query.name  + variables_str  + dumps_field(query)
        if self.format_gql:
            body = {
                    "type": "graphql",
                    "content": raw,
                    "options": {
                        "tabWidth": 4
                    }
                }

            proxies = {
                'https': proxy_url 
            }

            res = requests.post('https://www.345tool.com/api/format', body, proxies=proxies, verify=False)

            if res.status_code == 200:
                return res.json()['output']
            else:
                raise Exception('Formatting failed')
        else:
            return raw

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir')
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        os.makedirs(args.dir)

    gql_explorer = GQLExplorer(output_dir = args.dir)
