// AgentBazaar SDK — JavaScript Client Library
// npm install agentbazaar OR require from GitHub

const https = require('https');

class AgentBazaar {
  constructor(opts = {}) {
    this.baseUrl = opts.baseUrl || 'https://agentbazaar.tech';
    this.agentId = opts.agentId || null;
    this.apiKey = opts.apiKey || null;
  }

  async _request(method, path, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.baseUrl + path);
      const headers = { 'Content-Type': 'application/json' };
      if (this.agentId) headers['x-agent-id'] = this.agentId;
      if (this.apiKey) headers['x-api-key'] = this.apiKey;

      const req = https.request({
        hostname: url.hostname, path: url.pathname + (url.search || ''),
        method, headers, timeout: 60000
      }, (res) => {
        let d = '';
        res.on('data', c => d += c);
        res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { resolve(d); } });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }

  // ═══ Quick Start ═══
  async register(name, type, capabilities) {
    const r = await this._request('POST', '/v1/auto-connect', { name, type, capabilities });
    if (r.agent_id) { this.agentId = r.agent_id; this.apiKey = r.api_key; }
    return r;
  }

  async guide() { return this._request('GET', '/v1/for-ai'); }

  // ═══ Browse ═══
  async search(q, opts = {}) { return this._request('GET', `/v1/catalog?q=${encodeURIComponent(q)}&limit=${opts.limit || 20}${opts.liveOnly ? '&live_only=true' : ''}`); }
  async store(q) { return this._request('GET', `/v1/agent/store${q ? '?q=' + encodeURIComponent(q) : ''}`); }
  async models() { return this._request('GET', '/v1/models/free'); }
  async stats() { return this._request('GET', '/v1/stats'); }

  // ═══ Execute ═══
  async execute(input, opts = {}) {
    return this._request('POST', '/v1/execute', {
      input, provider: opts.provider || 'groq',
      model: opts.model || 'llama-3.3-70b-versatile', ...opts
    });
  }

  async smartInvoke(input, opts = {}) {
    return this._request('POST', '/v1/smart-invoke', { input, ...opts });
  }

  async chain(steps) { return this._request('POST', '/v1/execute/chain', { steps }); }

  async multimodal(task, opts = {}) {
    return this._request('POST', '/v1/multimodal/execute', { task, ...opts });
  }

  // ═══ Agent Build + Sell ═══
  async sellAuto(description) { return this._request('POST', '/v1/sell/auto', { description }); }
  
  async sellSmart(opts) { return this._request('POST', '/v1/sell/smart', opts); }

  async build(opts) { return this._request('POST', '/v1/agent/build', opts); }

  async runAgent(customId, input, variables) {
    return this._request('POST', `/v1/agent/run/${customId}`, { input, variables });
  }

  async chatAgent(customId, message, variables) {
    return this._request('POST', `/v1/agent/chat/${customId}`, { message, variables });
  }

  // ═══ Session + Memory ═══
  async createSession(name) { return this._request('POST', '/v1/session/create', { name }); }

  async chat(sessionId, input, opts = {}) {
    return this._request('POST', '/v1/session/execute', {
      session_id: sessionId, input, provider: opts.provider || 'groq', ...opts
    });
  }

  async setMemory(key, value) { return this._request('POST', '/v1/memory/set', { key, value }); }
  async getMemory(key) { return this._request('GET', `/v1/memory/get/${key}`); }

  // ═══ Data + Prompts ═══
  async uploadData(capability, content, title) {
    return this._request('POST', '/v1/data/upload', { capability, content, title });
  }

  async uploadPrompt(capability, content, title, variables) {
    return this._request('POST', '/v1/prompts/upload', { capability, content, title, variables });
  }

  async usePrompt(capability, variables, input, provider) {
    return this._request('POST', '/v1/prompts/use', { capability, variables, input, provider: provider || 'groq' });
  }

  // ═══ Autonomous ═══
  async setTrigger(customAgentId, type, config) {
    return this._request('POST', '/v1/autonomous/trigger', {
      custom_agent_id: customAgentId, trigger_type: type, config
    });
  }

  // ═══ Reputation ═══
  async reputation() { return this._request('GET', '/v1/reputation'); }
  async leaderboard() { return this._request('GET', '/v1/leaderboard'); }
}

module.exports = AgentBazaar;
