#!/bin/bash

# Build and test lightweight version for local testing
set -e

echo "🔨 Building lightweight Docker image for local testing..."

# Build the lightweight image
docker build -f terraform/inference/ray/Dockerfile.local \
  -t chai-ray-lightweight:latest \
  terraform/inference/ray/

echo "✅ Lightweight image built successfully!"
echo "🐳 Image size:"
docker images chai-ray-lightweight:latest

echo ""
echo "🧪 Testing basic functionality..."
echo "📝 This will test imports and basic vLLM setup without Ray Serve"

# Run the minimal test
docker run --rm \
  -e MODEL_ID="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T" \
  -e TENSOR_PARALLELISM="1" \
  -e MAX_MODEL_LEN="1024" \
  chai-ray-lightweight:latest \
  python -c "
import sys
sys.path.append('/app')
from test_vllm_minimal import main
import asyncio
asyncio.run(main())
"

echo ""
echo "🎉 Testing complete!"
echo "💡 The lightweight image should be much smaller than the full Ray image"



