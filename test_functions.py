import unittest
import sys
import os
import random
import json
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app modules for testing
import utils
from database import init_db, save_product, get_product, add_search_history, get_recent_searches, toggle_favorite, is_favorite

class TestAmazonUrlParser(unittest.TestCase):
    """Test ASIN extraction from different Amazon URL formats"""
    
    def test_standard_url(self):
        url = "https://www.amazon.com/dp/B07PXGQC1Q/"
        asin = utils.extract_asin(url)
        self.assertEqual(asin, "B07PXGQC1Q")
    
    def test_product_url(self):
        url = "https://www.amazon.com/Apple-AirPods-Pro-2nd-Generation/dp/B0BDHWDR12/"
        asin = utils.extract_asin(url)
        self.assertEqual(asin, "B0BDHWDR12")
    
    def test_short_url(self):
        url = "https://a.co/d/8iGnbpL"
        asin = utils.extract_asin(url)
        self.assertEqual(asin, "8iGnbpL")
    
    def test_invalid_url(self):
        url = "https://example.com"
        asin = utils.extract_asin(url)
        self.assertIsNone(asin)


class TestProductGeneration(unittest.TestCase):
    """Test product data generation and consistency"""
    
    def test_product_generation(self):
        """Test that product generation works and is consistent for the same ASIN"""
        asin = "B08N5KWB9H"
        api = None # Not needed for demo mode
        
        # Generate product twice with same ASIN
        product1 = utils.get_amazon_product_info(api, asin, demo_mode=True)
        product2 = utils.get_amazon_product_info(api, asin, demo_mode=True)
        
        # Assert products are not None
        self.assertIsNotNone(product1)
        self.assertIsNotNone(product2)
        
        # Assert titles are the same - verifies consistency
        self.assertEqual(product1['title'], product2['title'])
        
        # Price data should have the same pattern
        self.assertEqual(len(product1['price_data']), len(product2['price_data']))
        
        # Check that all required fields are present
        required_fields = ['title', 'price_data', 'current_price', 'peak_price', 'lowest_price', 'asin']
        for field in required_fields:
            self.assertIn(field, product1)
            self.assertIn(field, product2)
    
    def test_different_asins(self):
        """Test that different ASINs generate different products"""
        asin1 = "B08N5KWB9H"
        asin2 = "B09G9FPHY6"
        api = None # Not needed for demo mode
        
        product1 = utils.get_amazon_product_info(api, asin1, demo_mode=True)
        product2 = utils.get_amazon_product_info(api, asin2, demo_mode=True)
        
        # Assert products should have different titles
        self.assertNotEqual(product1['title'], product2['title'])


class TestGirlMathLogic(unittest.TestCase):
    """Test girl math calculations"""
    
    def test_girl_math_logic(self):
        """Test that girl math logic enhances savings"""
        current_price = 80.0
        peak_price = 100.0
        lowest_price = 75.0
        
        savings, percent = utils.girl_math_logic(current_price, peak_price, lowest_price)
        
        # Regular savings would be 20.0
        # Enhanced savings should be 20.0 * 1.1 = 22.0
        self.assertGreater(savings, 20.0)
        
        # Verify percentage calculation (100 - 80)/100 * 100 = 20%
        # Enhanced percentage should be 20 * 1.05 = 21%
        self.assertGreater(percent, 20.0)


class TestGirlMathStatement(unittest.TestCase):
    """Test girl math statement generation"""
    
    def test_statement_generation(self):
        """Test that girl math statements are generated based on price"""
        current_price = 80.0
        peak_price = 100.0
        lowest_price = 75.0
        
        # Import statement function from app
        try:
            from app import girl_math_statement
            statement = girl_math_statement(current_price, peak_price, lowest_price)
            
            # Verify a statement is returned
            self.assertIsNotNone(statement)
            self.assertTrue(isinstance(statement, str))
            self.assertGreater(len(statement), 10)  # Should be a meaningful sentence
        except ImportError:
            self.skipTest("girl_math_statement function not available in app.py")


class TestDatabaseFunctions(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        # Use an in-memory database for testing
        self.original_db_path = os.environ.get('DB_PATH', 'girlmath.db')
        os.environ['DB_PATH'] = ':memory:'
        init_db()
    
    def tearDown(self):
        """Restore original database path"""
        if self.original_db_path:
            os.environ['DB_PATH'] = self.original_db_path
        else:
            del os.environ['DB_PATH']
    
    def test_save_and_get_product(self):
        """Test saving and retrieving products"""
        product_info = {
            'asin': 'B08TEST123',
            'title': 'Test Product',
            'current_price': 99.99,
            'peak_price': 129.99,
            'lowest_price': 89.99,
            'price_data': [95.0, 100.0, 99.99],
            'category': 'test'
        }
        
        # Save product
        result = save_product(product_info)
        self.assertTrue(result)
        
        # Retrieve product
        retrieved = get_product('B08TEST123')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], 'Test Product')
        self.assertEqual(retrieved['current_price'], 99.99)
    
    def test_search_history(self):
        """Test adding and retrieving search history"""
        # Add to search history
        add_search_history(asin='B08TEST123', url='https://amazon.com/dp/B08TEST123')
        
        # Get recent searches
        searches = get_recent_searches()
        self.assertGreaterEqual(len(searches), 1)
    
    def test_favorites(self):
        """Test toggling favorites"""
        # Create a test product first
        product_info = {
            'asin': 'B08TEST456',
            'title': 'Test Favorite Product',
            'current_price': 49.99,
            'peak_price': 69.99,
            'lowest_price': 39.99,
            'price_data': [45.0, 50.0, 49.99],
            'category': 'test'
        }
        save_product(product_info)
        
        # Test that product is not a favorite initially
        self.assertFalse(is_favorite('B08TEST456'))
        
        # Add to favorites
        is_fav = toggle_favorite('B08TEST456', notes='Test notes')
        self.assertTrue(is_fav)
        
        # Verify it's now a favorite
        self.assertTrue(is_favorite('B08TEST456'))
        
        # Remove from favorites
        is_fav = toggle_favorite('B08TEST456')
        self.assertFalse(is_fav)
        
        # Verify it's not a favorite anymore
        self.assertFalse(is_favorite('B08TEST456'))


def run_tests():
    """Run all tests and return results as a report"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestAmazonUrlParser))
    test_suite.addTest(unittest.makeSuite(TestProductGeneration))
    test_suite.addTest(unittest.makeSuite(TestGirlMathLogic))
    test_suite.addTest(unittest.makeSuite(TestGirlMathStatement))
    test_suite.addTest(unittest.makeSuite(TestDatabaseFunctions))
    
    # Use TextTestRunner to capture output
    from io import StringIO
    test_output = StringIO()
    runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
    result = runner.run(test_suite)
    
    # Generate a report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'details': test_output.getvalue()
    }
    
    return report


def diagnostic_checks():
    """Run diagnostic checks on the application"""
    checks = {
        'timestamp': datetime.now().isoformat(),
        'checks': []
    }
    
    # Check 1: Can we extract ASINs properly?
    try:
        test_urls = [
            "https://www.amazon.com/dp/B07PXGQC1Q/",
            "https://a.co/d/8iGnbpL",
            "https://www.amazon.com/Apple-AirPods-Pro-2nd-Generation/dp/B0BDHWDR12/"
        ]
        results = []
        for url in test_urls:
            asin = utils.extract_asin(url)
            results.append({'url': url, 'asin': asin})
        
        checks['checks'].append({
            'name': 'ASIN Extraction',
            'status': 'success',
            'details': results
        })
    except Exception as e:
        checks['checks'].append({
            'name': 'ASIN Extraction',
            'status': 'failed',
            'error': str(e)
        })
    
    # Check 2: Can we generate product data?
    try:
        api = None
        asin = "B08N5KWB9H"
        product = utils.get_amazon_product_info(api, asin, demo_mode=True)
        
        if product:
            checks['checks'].append({
                'name': 'Product Generation',
                'status': 'success',
                'details': {
                    'title': product['title'],
                    'current_price': product['current_price'],
                    'price_data_length': len(product['price_data'])
                }
            })
        else:
            checks['checks'].append({
                'name': 'Product Generation',
                'status': 'failed',
                'error': 'No product data generated'
            })
    except Exception as e:
        checks['checks'].append({
            'name': 'Product Generation',
            'status': 'failed',
            'error': str(e)
        })
    
    # Check 3: Database connectivity
    try:
        # Initialize DB (should be safe to call multiple times)
        init_db()
        
        # Create a test product to check DB write access
        test_product = {
            'asin': f'TEST{random.randint(1000, 9999)}',
            'title': 'Test Product',
            'current_price': 99.99,
            'peak_price': 129.99,
            'lowest_price': 89.99,
            'price_data': [95.0, 100.0, 99.99]
        }
        
        saved = save_product(test_product)
        
        if saved:
            checks['checks'].append({
                'name': 'Database Access',
                'status': 'success',
                'details': 'Database connection working'
            })
        else:
            checks['checks'].append({
                'name': 'Database Access',
                'status': 'failed',
                'error': 'Could not save to database'
            })
    except Exception as e:
        checks['checks'].append({
            'name': 'Database Access',
            'status': 'failed',
            'error': str(e)
        })
    
    return checks


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--diagnostic':
        print(json.dumps(diagnostic_checks(), indent=2))
    else:
        report = run_tests()
        print(json.dumps(report, indent=2))
        
        # Also display a readable summary
        print(f"\nTest Summary:")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failures']}")
        print(f"Errors: {report['errors']}")