"""
Lib for creating standardized response from this component.
"""

from flask import make_response, jsonify, Response
import json


def make_json_response(status_code, data, links=None, meta=None):
    """
    Create a standardized json response.
    At least one of `data` or `meta` must not be None.
    """
    result_json = {
        'status': status_code
    }

    if data is not None:
        result_json['data'] = data
    if links is not None:
        result_json['links'] = links
    if meta is not None:
        result_json['meta'] = meta

    return make_response(jsonify(result_json), status_code)


def make_streamed_response(status_code, data_generator, content_type='application/json'):
    return Response(
        data_generator, content_type=content_type, status=status_code)


def make_streamed_json_response(status_code, data_generator, links=None, meta=None):
    def generate(status_code, data_generator, links, meta):
        yield '{{"status":{}{}{}, "data": '.format(
            status_code,
            ', "links": {}'.format(json.dumps(links)) if links is not None else '',
            ', "meta": {}'.format(json.dumps(meta)) if meta is not None else ''
        )
        try:
            yield next(data_generator)
        except StopIteration:
            # StopIteration here means the length was zero, so yield a valid releases doc and stop
            yield '[]}'
            return

        # Iterate over the data
        for chunk in data_generator:
            yield chunk

        yield '}'

    return make_streamed_response(
        status_code,
        generate(status_code, data_generator, links, meta),
        content_type='application/json')
