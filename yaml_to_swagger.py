#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import yaml
import argparse

from sample import sample_object

types = {
    'datetime': 'string',
    'list': 'array',
    'dict': 'object'
}

fields = {
    'allowed': 'enum',
    'maxlength': 'maxLength',
    'minlength': 'minLength'
}


def convert_to_swagger_yaml(yaml_file, object_name):
    properties = {}

    swagger_yaml = {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "Simple API"
        },
        "paths": {
            "/": {
                "get": {
                    "responses": {
                        "200": {"description": "Successful Operation", "schema": {"$ref": "#/definitions/{0}".format(object_name)}}
                    }
                }
            }
        },
        "definitions": {
            object_name: {
                "type": "object",
                "required": ['rating'],
                "properties": properties
            }
        }
    }

    with open(yaml_file) as f:
        yaml_data = yaml.load(f)

    for key, value in yaml_data.items():
        d_type = types.get(value['type'], value['type'])
        if d_type in ['string', 'integer', 'boolean']:
            properties[key] = dict(type=d_type, example=sample_object.get(key, ''))

            for k, v in fields.items():
                if value.get(k):
                    properties[key][v] = value[k]

    return swagger_yaml


def main(args):
    yaml_file = args.yaml_file
    if not os.path.exists(yaml_file):
        sys.exit("Yaml file: {0} not found".format(yaml_file))

    swagger_yaml = convert_to_swagger_yaml(yaml_file, args.object_name)

    print json.dumps(swagger_yaml)


if __name__ == "__main__":
    '''
    '''
    parser = argparse.ArgumentParser(description='Convert yaml to swagger yaml')

    parser.add_argument('yaml_file', help='yaml file to covert to swagger yaml')

    parser.add_argument('object_name', help='name of the object')

    args = parser.parse_args()

    main(args)
