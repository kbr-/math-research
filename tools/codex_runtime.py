#!/usr/bin/env python3
"""Small authenticated client of the existing local Codex daemon (no daemon startup)."""
import asyncio
from collections import deque
import json
import subprocess


class NativeError(RuntimeError):
    pass


class Client:
    """Single-consumer RPC connection. Retain interleaved events, refuse approval requests."""
    def __init__(self, socket):
        self.socket = socket
        self.sequence = 0
        self.events = deque()

    @classmethod
    async def connect(cls):
        import websockets
        process = await asyncio.create_subprocess_exec(
            'codex', 'app-server', 'daemon', 'version', stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        try:
            output, error = await asyncio.wait_for(process.communicate(), 2)
        except BaseException:
            if process.returncode is None:
                process.kill()
            await process.wait()
            raise
        if process.returncode:
            raise NativeError('Existing Codex daemon unavailable: ' + error.decode(errors='replace'))
        address = json.loads(output)['socketPath']
        socket = await websockets.unix_connect(address, uri='ws://localhost',
                                              open_timeout=2, close_timeout=.1, max_size=16*1024*1024)
        client = cls(socket)
        try:
            await asyncio.wait_for(client.call('initialize', {
                'clientInfo': {'name': 'noemesis_framework', 'version': '1'},
                'capabilities': {'experimentalApi': True}}), 2)
            await socket.send(json.dumps({'method': 'initialized', 'params': {}}))
        except BaseException:
            await socket.close()
            raise
        return client

    async def receive(self):
        while True:
            message = json.loads(await self.socket.recv())
            if 'id' in message and 'method' in message:
                await self.socket.send(json.dumps({'id': message['id'], 'error': {
                    'code': -32000, 'message': 'Framework controllers cannot grant approvals'}}))
                continue
            return message

    async def call(self, method, params):
        self.sequence += 1
        ident = self.sequence
        await self.socket.send(json.dumps({'id': ident, 'method': method, 'params': params}))
        while True:
            message = await self.receive()
            if message.get('id') == ident:
                if 'error' in message:
                    raise NativeError(method + ': ' + json.dumps(message['error']))
                return message['result']
            if 'id' not in message:
                self.events.append(message)

    async def event(self):
        return self.events.popleft() if self.events else await self.receive()

    async def turn(self, thread, text, effort, schema=None):
        params = {'threadId': thread, 'input': [{'type': 'text', 'text': text}], 'effort': effort}
        if schema is not None:
            params['outputSchema'] = schema
        started = await self.call('turn/start', params)
        turn = started['turn']['id']
        messages = []
        try:
            while True:
                event = await self.event()
                data = event.get('params', {})
                if data.get('threadId') != thread:
                    continue
                if event.get('method') == 'item/completed' and data.get('turnId') == turn:
                    item = data['item']
                    if item.get('type') == 'agentMessage':
                        messages.append(item['text'])
                if event.get('method') == 'turn/completed' and data['turn']['id'] == turn:
                    if data['turn']['status'] != 'completed':
                        raise NativeError('Native turn ended: ' + data['turn']['status'])
                    return '\n'.join(messages)
        except BaseException:
            # Interrupt only this controller's turn; bounded even when the daemon has failed.
            try:
                await asyncio.wait_for(self.call('turn/interrupt', {
                    'threadId': thread, 'turnId': turn}), .15)
            except Exception:
                pass
            raise

    async def isolation_config(self, cwd, effort, tools=True):
        effective = await self.call('config/read', {'cwd': str(cwd), 'includeLayers': False})
        servers = effective['config'].get('mcp_servers') or {}
        if not isinstance(servers, dict):
            raise NativeError('Cannot establish configured MCP server isolation')
        config = isolated_config(effort, tools=tools)
        config['mcp_servers'] = {name: {'enabled': False} for name in servers}
        return config

    async def close(self):
        await self.socket.close()


def isolated_config(effort, tools=True):
    config = {'model_reasoning_effort': effort, 'features.hooks': False,
              'features.apps': False, 'features.plugins': False, 'agents.enabled': False,
              'features.browser_use': False, 'features.computer_use': False,
              'web_search': 'disabled', 'project_doc_max_bytes': 0}
    if not tools:
        config.update({'features.shell_tool': False, 'features.unified_exec': False})
    return config


def verify_isolation(response, effort):
    if (response.get('reasoningEffort') != effort or response.get('approvalPolicy') != 'never'
            or response.get('sandbox', {}).get('type') != 'readOnly'
            or response['sandbox'].get('networkAccess') is not False):
        raise NativeError('Codex did not apply the required effort/read-only/no-approval policy')
