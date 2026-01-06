import os
import sys
import tempfile

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mocks'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

import vim
from utils import load_provider


def test_load_provider_defines_file_variable():
    """Test that __file__ is defined when loading a provider script via py3file"""
    
    # Create a temporary provider script that uses __file__
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        provider_script = f.name
        f.write("""
import os

# This should not raise NameError because __file__ should be defined
test_py_dir = os.path.dirname(__file__)

class TestProvider:
    def __init__(self):
        self.name = "test"
        self.file_location = __file__
""")
    
    try:
        # Mock the vim.eval to return provider config
        original_eval = vim.eval
        
        def mock_eval(cmd):
            if cmd == "g:vim_ai_providers":
                return {
                    'test': {
                        'script_path': provider_script,
                        'class_name': 'TestProvider'
                    }
                }
            return original_eval(cmd)
        
        vim.eval = mock_eval
        
        # This should not raise an error
        provider_class = load_provider('test')
        
        # Verify the provider class was loaded
        assert provider_class is not None
        assert provider_class.__name__ == 'TestProvider'
        
        # Create an instance to verify __file__ was accessible
        instance = provider_class()
        assert instance.file_location == provider_script
        
        # Restore original eval
        vim.eval = original_eval
        
    finally:
        # Clean up temp file
        if os.path.exists(provider_script):
            os.unlink(provider_script)


def test_load_provider_with_openai_style_file_usage():
    """Test that provider scripts can use __file__ like openai.py does"""
    
    # Create a temporary provider script that uses __file__ similar to openai.py
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        provider_script = f.name
        f.write("""
import os
import sys

# This is similar to how openai.py uses __file__
py_dir = os.path.dirname(os.path.dirname(__file__))

class OpenAILikeProvider:
    def __init__(self):
        self.py_dir = py_dir
""")
    
    try:
        # Mock the vim.eval to return provider config
        original_eval = vim.eval
        
        def mock_eval(cmd):
            if cmd == "g:vim_ai_providers":
                return {
                    'openai-like': {
                        'script_path': provider_script,
                        'class_name': 'OpenAILikeProvider'
                    }
                }
            return original_eval(cmd)
        
        vim.eval = mock_eval
        
        # This should not raise an error
        provider_class = load_provider('openai-like')
        
        # Verify the provider class was loaded
        assert provider_class is not None
        
        # Create an instance to verify __file__ manipulation worked
        instance = provider_class()
        expected_py_dir = os.path.dirname(os.path.dirname(provider_script))
        assert instance.py_dir == expected_py_dir
        
        # Restore original eval
        vim.eval = original_eval
        
    finally:
        # Clean up temp file
        if os.path.exists(provider_script):
            os.unlink(provider_script)


if __name__ == '__main__':
    print("Running test_load_provider_defines_file_variable...")
    test_load_provider_defines_file_variable()
    print("PASS: test_load_provider_defines_file_variable")
    
    print("Running test_load_provider_with_openai_style_file_usage...")
    test_load_provider_with_openai_style_file_usage()
    print("PASS: test_load_provider_with_openai_style_file_usage")
    
    print("\nAll tests passed!")
