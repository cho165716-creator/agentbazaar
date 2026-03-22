# AgentBazaar SDK (Python)

AI Agent Marketplace — Search, execute, build, and sell AI agents.

## Install
```
pip install agentbazaar
```

## Quick Start
```python
from agentbazaar import AgentBazaar

bazaar = AgentBazaar()
bazaar.register('my-ai', 'Assistant', ['chat'])

# Execute free AI
result = bazaar.execute('Translate to Korean: Hello world')
print(result)

# Search agents
agents = bazaar.search('translation')

# Build and sell
bazaar.sell_auto('Translates any text to Korean')

# Chat with memory
session = bazaar.create_session('my-chat')
bazaar.chat(session['session_id'], 'My name is Alex')
bazaar.chat(session['session_id'], 'What is my name?')  # "Alex"
```

## Docs
https://agentbazaar.tech/v1/for-ai
