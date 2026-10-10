#!/usr/bin/env python3
"""Disposable standard-library MCP fixture for native evidence-capture acceptance."""
import json
import sys

for line in sys.stdin:
    message = json.loads(line)
    if 'id' not in message:
        continue
    method = message['method']
    if method == 'initialize':
        result = {'protocolVersion': message['params']['protocolVersion'],
                  'capabilities': {'tools': {}}, 'serverInfo': {'name': 'parity-probe', 'version': '1'}}
    elif method == 'tools/list':
        result = {'tools': [{'name': 'lookup_capability', 'description': 'Read the synthetic fixture capability.',
            'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False},
            'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}]}
    elif method == 'tools/call' and message['params']['name'] == 'lookup_capability':
        result = {'content': [{'type': 'text', 'text': 'The synthetic capability is available.'}]}
    else:
        print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32601, 'message': 'Unknown fixture method'}}), flush=True)
        continue
    print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}), flush=True)
