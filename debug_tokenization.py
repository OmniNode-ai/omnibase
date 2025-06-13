#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from omnibase.nodes.node_manager.v1_0_0.models.model_template_context import ModelTemplateContext

context = ModelTemplateContext(
    node_name='node_runtime',
    node_class='NodeRuntimeNode', 
    node_id='node_runtime',
    node_id_upper='NODE_RUNTIME',
    author='System Architecture Team',
    year=2025,
    description='Runtime coordination node'
)

print('Context fields:')
for key, value in context.model_dump(exclude_none=True).items():
    token = f'{{{key.upper()}}}'
    print(f'  {key} -> {token} = {value}')

# Test replacement
test_content = "class {NODE_CLASS}(ProtocolReducer):"
print(f'\nOriginal: {test_content}')

for key, value in context.model_dump(exclude_none=True).items():
    token = f'{{{key.upper()}}}'
    test_content = test_content.replace(token, str(value))
    print(f'After {token}: {test_content}') 