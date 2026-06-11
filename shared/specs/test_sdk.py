# Auto-generated E2E Integration Test Suite
import unittest
import sys
import os

# Ensure specs folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sdk import ShinyFishstickSiteSDK

class TestShinyFishstickE2E(unittest.TestCase):

    def test_purchase_flow(self):
        """Test workflow: End-to-end purchasing workflow from login to order confirmation"""
        sdk = ShinyFishstickSiteSDK("http://localhost:8001")
        print("Launching Playwright E2E SDK...", flush=True)
        sdk.start(headless=True)
        try:
            # Step 0: login
            print('Executing login...', flush=True)
            sdk.login('admin@example.com', 'password123')
            # Step 1: search_products
            print('Executing search_products...', flush=True)
            sdk.search_products('Quantum')
            # Step 2: add_to_cart
            print('Executing add_to_cart...', flush=True)
            res = sdk.add_to_cart('2')
            self.assertIsNotNone(res)
            self.assertEqual(res.get('status'), 'success')
            # Step 3: checkout
            print('Executing checkout...', flush=True)
            sdk.checkout()
            print("Workflow test_purchase_flow passed successfully!", flush=True)
        finally:
            sdk.close()


if __name__ == "__main__":
    unittest.main()
