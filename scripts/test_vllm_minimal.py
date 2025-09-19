#!/usr/bin/env python3
"""
Minimal test script for vLLM functionality
Tests the core chat completion logic without Ray Serve
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the ray directory to Python path
ray_dir = Path(__file__).parent.parent / "terraform" / "inference" / "ray"
sys.path.insert(0, str(ray_dir))

async def test_vllm_basic():
    """Test basic vLLM functionality"""
    try:
        print("🧪 Testing vLLM basic functionality...")
        
        # Import the core components
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.engine.async_llm_engine import AsyncLLMEngine
        
        print("✅ Successfully imported vLLM components")
        
        # Test with minimal configuration
        config = {
            "model": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
            "tensor-parallel-size": "1",
            "max-model-len": "1024",  # Very small for testing
            "gpu-memory-utilization": "0.1",  # Use minimal GPU memory
            "max-num-batched-tokens": "512",  # Small batch size
        }
        
        print(f"📝 Using config: {config}")
        
        # Parse arguments
        from serve_chat_completion import parse_vllm_args
        parsed_args = parse_vllm_args(config)
        engine_args = AsyncEngineArgs.from_cli_args(parsed_args)
        
        # Set minimal settings for testing
        engine_args.worker_use_ray = False  # Don't use Ray for local testing
        engine_args.trust_remote_code = True
        engine_args.enable_chunked_prefill = False  # Disable for simpler testing
        
        print("✅ Engine args configured successfully")
        
        # Test if we can create the engine (this will download the model if needed)
        print("🚀 Creating AsyncLLMEngine...")
        engine = AsyncLLMEngine.from_engine_args(engine_args)
        print("✅ AsyncLLMEngine created successfully!")
        
        # Test basic model info
        model_config = await engine.get_model_config()
        print(f"📊 Model config: {model_config}")
        
        # Clean up
        await engine.engine.terminate()
        print("✅ Engine terminated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test if all required imports work"""
    try:
        print("🧪 Testing imports...")
        
        # Test basic imports
        import fastapi
        import starlette
        import vllm
        import transformers
        
        print("✅ All basic imports successful")
        
        # Test our custom imports
        from serve_chat_completion import VLLMDeployment, build_app, parse_vllm_args
        print("✅ Custom module imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Minimal vLLM Functionality Test")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("❌ Import tests failed")
        return
    
    # Test basic vLLM functionality
    if await test_vllm_basic():
        print("\n🎉 All tests passed! Basic vLLM functionality is working.")
        print("\n💡 You can now test the full Ray Serve application if needed.")
    else:
        print("\n❌ Basic vLLM test failed.")

if __name__ == "__main__":
    asyncio.run(main())



