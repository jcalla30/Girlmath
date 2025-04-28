#!/usr/bin/env python3
"""
Test runner for Girl Math Deal Finder app.
Run this script to verify the app is functioning correctly.
"""

import json
from test_functions import run_tests, diagnostic_checks

if __name__ == "__main__":
    print("Running diagnostic checks...")
    diagnostics = diagnostic_checks()
    
    # Print diagnostics summary
    print("\n=== DIAGNOSTIC RESULTS ===")
    for check in diagnostics['checks']:
        status = "✅" if check['status'] == 'success' else "❌"
        print(f"{status} {check['name']}")
    
    print("\nRunning tests...")
    test_results = run_tests()
    
    # Print test summary 
    print("\n=== TEST RESULTS ===")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failures']}")
    print(f"Errors: {test_results['errors']}")
    
    # Generate detailed report
    with open("test_report.json", "w") as f:
        report = {
            "diagnostics": diagnostics,
            "tests": test_results
        }
        json.dump(report, f, indent=2)
    
    print("\nDetailed test results saved to test_report.json")
    
    # Exit with appropriate code
    if test_results['failures'] > 0 or test_results['errors'] > 0:
        print("\n❌ Some tests failed. Please check the errors above.")
        exit(1)
    else:
        print("\n✅ All tests passed!")
        exit(0)