#!/bin/bash

# Test script for running Ray Serve application locally
# Make sure you have built the Docker image first

set -e

echo "🚀 Starting Ray Serve application locally..."

# Set environment variables for local testing
export MODEL_ID="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T"
export TENSOR_PARALLELISM="1"  # Use 1 for local testing
export MAX_MODEL_LEN="2048"    # Smaller for local testing
export VLLM_ENABLE_AUTO_TOOL_CHOICE="false"  # Disable for simpler testing

# Run the Docker container
docker run -it --rm \
  -p 8000:8000 \
  -e MODEL_ID="$MODEL_ID" \
  -e TENSOR_PARALLELISM="$TENSOR_PARALLELISM" \
  -e MAX_MODEL_LEN="$MAX_MODEL_LEN" \
  -e VLLM_ENABLE_AUTO_TOOL_CHOICE="$VLLM_ENABLE_AUTO_TOOL_CHOICE" \
  --name chai-ray-local \
  us-central1-docker.pkg.dev/gcp-home-dtian01/chatapp-docker-repo/llama-ray-serve:latest \
  python -c "
import ray
ray.init()
from serve_chat_completion import build_app
app = build_app()
ray.serve.run(app, host='0.0.0.0', port=8000)
print('✅ Ray Serve application started on port 8000')
print('📝 Health check: http://localhost:8000/-/healthz')
print('🤖 Chat endpoint: http://localhost:8000/v1/chat/completions')
ray.shutdown()
"

echo "✅ Container started successfully!"
echo "📝 Health check: http://localhost:8000/-/healthz"
echo "🤖 Chat endpoint: http://localhost:8000/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the container"
