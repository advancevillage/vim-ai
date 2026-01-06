import os
import sys
import tempfile

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mocks'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

def test_file_variable_is_available_in_script():
    """Test that __file__ can be accessed in a script when it's set in globals"""
    
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
        # Simulate what load_provider does
        namespace = {'__file__': provider_script}
        
        # Execute the script with __file__ defined
        with open(provider_script, 'r') as f:
            script_content = f.read()
            exec(script_content, namespace)
        
        # Verify the provider class was loaded
        assert 'TestProvider' in namespace
        provider_class = namespace['TestProvider']
        
        # Create an instance to verify __file__ was accessible
        instance = provider_class()
        assert instance.file_location == provider_script
        
        print('PASS: test_file_variable_is_available_in_script')
        
    finally:
        # Clean up temp file
        if os.path.exists(provider_script):
            os.unlink(provider_script)


def test_openai_style_file_usage():
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
        # Simulate what load_provider does
        namespace = {'__file__': provider_script}
        
        # Execute the script with __file__ defined
        with open(provider_script, 'r') as f:
            script_content = f.read()
            exec(script_content, namespace)
        
        # Verify the provider class was loaded
        assert 'OpenAILikeProvider' in namespace
        provider_class = namespace['OpenAILikeProvider']
        
        # Create an instance to verify __file__ manipulation worked
        instance = provider_class()
        expected_py_dir = os.path.dirname(os.path.dirname(provider_script))
        assert instance.py_dir == expected_py_dir
        
        print('PASS: test_openai_style_file_usage')
        
    finally:
        # Clean up temp file
        if os.path.exists(provider_script):
            os.unlink(provider_script)


def test_file_cleanup_after_load():
    """Test that __file__ is properly cleaned up after provider load"""
    
    # Simulate globals before load
    test_globals = {'existing_var': 'test'}
    
    # Simulate the load_provider logic
    original_file = test_globals.get('__file__')
    assert original_file is None
    
    provider_path = '/test/provider.py'
    test_globals['__file__'] = provider_path
    
    # Simulate script execution
    test_code = 'py_dir = "success"'
    exec(test_code, test_globals)
    
    # Restore (cleanup)
    if original_file is not None:
        test_globals['__file__'] = original_file
    elif '__file__' in test_globals:
        del test_globals['__file__']
    
    # Verify cleanup worked
    assert '__file__' not in test_globals
    assert test_globals.get('py_dir') == 'success'
    assert test_globals.get('existing_var') == 'test'
    
    print('PASS: test_file_cleanup_after_load')


if __name__ == '__main__':
    print("Running test_file_variable_is_available_in_script...")
    test_file_variable_is_available_in_script()
    
    print("Running test_openai_style_file_usage...")
    test_openai_style_file_usage()
    
    print("Running test_file_cleanup_after_load...")
    test_file_cleanup_after_load()
    
    print("\nAll tests passed!")

