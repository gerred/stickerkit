#!/bin/bash

# Workflow Debugging Script
# Helps debug ComfyUI workflows with detailed logging

set -e

WORKFLOW_FILE=${1:-"workflows/examples/basic_flux.json"}

echo "🔍 Debugging ComfyUI Workflow"
echo "Workflow file: $WORKFLOW_FILE"

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Workflow file not found: $WORKFLOW_FILE"
    echo "Available workflows:"
    find workflows -name "*.json" -type f
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

echo "📋 Validating workflow structure..."
python -c "
import json
import sys

try:
    with open('$WORKFLOW_FILE', 'r') as f:
        workflow = json.load(f)
    
    print(f'✅ Valid JSON structure')
    print(f'Nodes: {len(workflow)}')
    
    # Check for required fields
    for node_id, node in workflow.items():
        if 'class_type' not in node:
            print(f'❌ Node {node_id} missing class_type')
            sys.exit(1)
        if 'inputs' not in node:
            print(f'❌ Node {node_id} missing inputs')
            sys.exit(1)
    
    print('✅ All nodes have required fields')
    
    # List node types
    node_types = set(node['class_type'] for node in workflow.values())
    print(f'Node types used: {sorted(node_types)}')
    
except json.JSONDecodeError as e:
    print(f'❌ Invalid JSON: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

echo "🔧 Testing workflow execution..."
cd ComfyUI

python -c "
import sys
sys.path.append('.')
import json
from nodes import NODE_CLASS_MAPPINGS
from execution import validate_inputs, execute

# Load workflow
with open('../$WORKFLOW_FILE', 'r') as f:
    workflow = json.load(f)

print('🧪 Validating inputs...')
try:
    validation_result = validate_inputs(workflow, NODE_CLASS_MAPPINGS)
    if validation_result[0]:
        print('✅ Workflow validation passed')
    else:
        print(f'❌ Validation failed: {validation_result[1]}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Validation error: {e}')
    sys.exit(1)

print('🎯 Workflow is ready for execution')
"

cd ..

echo ""
echo "✅ Workflow debugging complete!"
echo ""
echo "To execute this workflow:"
echo "1. Start ComfyUI server: ./scripts/start-comfyui.sh"
echo "2. Load workflow in web UI: http://127.0.0.1:8188"
echo "3. Or use API: curl -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' -d @$WORKFLOW_FILE"
