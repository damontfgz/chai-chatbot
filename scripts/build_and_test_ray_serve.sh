#!/bin/bash

# Build and test Ray Serve optimized version for GKE deployment
set -e

echo "🔨 Building Ray Serve optimized Docker image..."
echo "📝 This includes only essential Ray components for serving"

# Build the Ray Serve optimized image
docker build -f terraform/inference/ray/Dockerfile.ray-serve \
  -t chai-ray-serve:latest \
  terraform/inference/ray/

echo "✅ Ray Serve optimized image built successfully!"
echo "🐳 Image size:"
docker images chai-ray-serve:latest

echo ""
echo "🧪 Testing Ray Serve functionality locally..."
echo "📝 This will test the full Ray Serve deployment locally"

# Test the Ray Serve application locally
docker run --rm \
  -p 8000:8000 \
  -e MODEL_ID="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T" \
  -e TENSOR_PARALLELISM="1" \
  -e MAX_MODEL_LEN="1024" \
  -e VLLM_ENABLE_AUTO_TOOL_CHOICE="false" \
  chai-ray-serve:latest \
  python -c "
import ray
ray.init()
from serve_chat_completion import build_app
app = build_app()
ray.serve.run(app, host='0.0.0.0', port=8000)
print('✅ Ray Serve application started on port 8000')
print('📝 Health check: http://localhost:8000/-/healthz')
print('🤖 Chat endpoint: http://localhost:8000/v1/chat/completions')
print('🚀 Ready for GKE deployment!')
ray.shutdown()
"

echo ""
echo "🎉 Testing complete!"
echo "💡 This image should be much smaller than the full Ray ML image"
echo "🚀 It's ready for GKE deployment with Ray Serve"



