import pytest
import sys

def run_tests():
    print("====================================================")
    print("           Running Memora Automated Tests           ")
    print("====================================================")
    
    # Run pytest on the tests/ directory
    retcode = pytest.main(["-v", "tests/"])
    
    print("====================================================")
    if retcode == 0:
        print("          All Tests Passed Successfully! (100%)    ")
    else:
        print(f"          Tests Failed with exit code {retcode}    ")
    print("====================================================")
    sys.exit(retcode)

if __name__ == "__main__":
    run_tests()
