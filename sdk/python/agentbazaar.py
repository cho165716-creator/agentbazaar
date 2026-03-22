"""AgentBazaar SDK — Python Client Library"""
import json, urllib.request, urllib.parse

class AgentBazaar:
    def __init__(self, agent_id=None, api_key=None, base_url='https://agentbazaar.tech'):
        self.base_url = base_url
        self.agent_id = agent_id
        self.api_key = api_key

    def _request(self, method, path, body=None):
        url = self.base_url + path
        headers = {'Content-Type': 'application/json'}
        if self.agent_id: headers['x-agent-id'] = self.agent_id
        if self.api_key: headers['x-api-key'] = self.api_key
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {'error': str(e)}

    # Quick Start
    def register(self, name, type='AI Agent', capabilities=None):
        r = self._request('POST', '/v1/auto-connect', {'name': name, 'type': type, 'capabilities': capabilities or ['general']})
        if 'agent_id' in r: self.agent_id, self.api_key = r['agent_id'], r['api_key']
        return r

    def guide(self): return self._request('GET', '/v1/for-ai')

    # Browse
    def search(self, q, limit=20): return self._request('GET', f'/v1/catalog?q={urllib.parse.quote(q)}&limit={limit}')
    def store(self, q=None): return self._request('GET', f'/v1/agent/store{"?q="+urllib.parse.quote(q) if q else ""}')
    def models(self): return self._request('GET', '/v1/models/free')
    def stats(self): return self._request('GET', '/v1/stats')

    # Execute
    def execute(self, input, provider='groq', model='llama-3.3-70b-versatile', **kw):
        return self._request('POST', '/v1/execute', {'input': input, 'provider': provider, 'model': model, **kw})

    def smart_invoke(self, input, agent_id=None, capability=None):
        return self._request('POST', '/v1/smart-invoke', {'input': input, 'agent_id': agent_id, 'capability': capability})

    def chain(self, steps): return self._request('POST', '/v1/execute/chain', {'steps': steps})

    def multimodal(self, task, **kw): return self._request('POST', '/v1/multimodal/execute', {'task': task, **kw})

    # Build + Sell
    def sell_auto(self, description): return self._request('POST', '/v1/sell/auto', {'description': description})
    def sell_smart(self, **kw): return self._request('POST', '/v1/sell/smart', kw)
    def build(self, **kw): return self._request('POST', '/v1/agent/build', kw)
    def run_agent(self, custom_id, input, variables=None):
        return self._request('POST', f'/v1/agent/run/{custom_id}', {'input': input, 'variables': variables})
    def chat_agent(self, custom_id, message, variables=None):
        return self._request('POST', f'/v1/agent/chat/{custom_id}', {'message': message, 'variables': variables})

    # Session + Memory
    def create_session(self, name='default'): return self._request('POST', '/v1/session/create', {'name': name})
    def chat(self, session_id, input, provider='groq', **kw):
        return self._request('POST', '/v1/session/execute', {'session_id': session_id, 'input': input, 'provider': provider, **kw})
    def set_memory(self, key, value): return self._request('POST', '/v1/memory/set', {'key': key, 'value': value})
    def get_memory(self, key): return self._request('GET', f'/v1/memory/get/{key}')

    # Data + Prompts
    def upload_data(self, capability, content, title=None):
        return self._request('POST', '/v1/data/upload', {'capability': capability, 'content': content, 'title': title})
    def upload_prompt(self, capability, content, title=None, variables=None):
        return self._request('POST', '/v1/prompts/upload', {'capability': capability, 'content': content, 'title': title, 'variables': variables})
    def use_prompt(self, capability, variables=None, input=None, provider='groq'):
        return self._request('POST', '/v1/prompts/use', {'capability': capability, 'variables': variables, 'input': input, 'provider': provider})

    # Autonomous
    def set_trigger(self, custom_agent_id, trigger_type, config):
        return self._request('POST', '/v1/autonomous/trigger', {'custom_agent_id': custom_agent_id, 'trigger_type': trigger_type, 'config': config})

    # Reputation
    def reputation(self): return self._request('GET', '/v1/reputation')
    def leaderboard(self): return self._request('GET', '/v1/leaderboard')
