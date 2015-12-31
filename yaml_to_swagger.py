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


def update_definitions(definitions, data, name, sample):
    properties = {}
    required = []

    definition_schema = {
        "type": "object",
        "required": required,
        "properties": properties
    }

    for key, value in data.items():
        if value.get('required'):
            required.append(key)

        d_type = types.get(value['type'], value['type'])

        if d_type in ['string', 'integer', 'boolean']:
            properties[key] = dict(type=d_type, example=sample.get(key, ''))
            for k, v in fields.items():
                if value.get(k):
                    properties[key][v] = value[k]
        elif d_type == "object":
            properties[key] = {"$ref": "#/definitions/{0}".format(key)}
            if value.get("schema"):
                update_definitions(definitions, value['schema'], key, sample.get(key) or {})
            else:
                definitions[key] = {"type": "object"}
        elif d_type == "array":
            if value.get('schema'):
                if value['schema'].get('schema'):
                    properties[key] = {"type": d_type, "items": {"$ref": "#/definitions/{0}".format(key)}}
                    update_definitions(definitions, value['schema']['schema'], key, sample[key][0] if sample[key] else {})
                else:
                    d = {"type": d_type, "items": {"type": value["schema"]["type"]}}
                    if sample[key]:
                        d["items"]["example"] = sample[key][0]
                    properties[key] = d
            else:
                properties[key] = {"type": d_type, "items": {"$ref": "#/definitions/{0}".format(key)}}
                definitions[key] = {"type": "object"}

    definitions[name] = definition_schema


def convert_to_swagger_yaml(yaml_file, object_name):
    definitions = {}

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
                        "200": {
                            "description": "Successful Operation",
                            "schema": {
                                "$ref": "#/definitions/{0}".format(object_name)
                            }
                        }
                    }
                }
            }
        }
    }

    with open(yaml_file) as f:
        yaml_data = yaml.load(f)

    update_definitions(definitions, yaml_data, object_name, sample_object)

    swagger_yaml["definitions"] = definitions

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
