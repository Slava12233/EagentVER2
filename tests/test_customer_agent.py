import pytest
import time
import logging
import random
import string
from datetime import datetime

# Disable insecure HTTPS warnings that might appear when testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCustomerAgent:
    """Test suite for the Customer Agent functionality."""
    
    created_customers = []  # Track customers created during tests for cleanup
    
    @pytest.fixture(autouse=True)
    def cleanup_created_customers(self, request):
        """Fixture to clean up any customers created during tests."""
        yield
        
        # Skip cleanup if there's nothing to clean
        if not self.created_customers:
            return
            
        logger.info(f"Cleaning up {len(self.created_customers)} customers created during tests")
        for customer_id in self.created_customers:
            try:
                response = request.getfixturevalue("customer_agent").delete_customer(customer_id)
                if "הלקוח נמחק בהצלחה" in response or "successfully deleted" in response.lower():
                    logger.info(f"Cleaned up customer ID: {customer_id}")
                else:
                    logger.warning(f"Failed to clean up customer ID: {customer_id}. Response: {response}")
            except Exception as e:
                logger.error(f"Error cleaning up customer ID {customer_id}: {str(e)}")
        
        # Clear the list after cleanup attempt
        self.created_customers.clear()
    
    def generate_unique_email(self):
        """Generate a unique email for testing."""
        timestamp = int(time.time())
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        return f"test{timestamp}{random_chars}@example.com"
    
    def test_agent_initialization(self, customer_agent):
        """Test that the customer agent initializes correctly."""
        assert customer_agent is not None
        assert hasattr(customer_agent, 'woocommerce')
        assert hasattr(customer_agent, 'function_map')
        
        # Check if required functions are available
        assert 'list_customers' in customer_agent.function_map
        assert 'create_customer' in customer_agent.function_map
        assert 'get_customer_by_id' in customer_agent.function_map
        assert 'update_customer' in customer_agent.function_map
        assert 'delete_customer' in customer_agent.function_map
        assert 'search_customers' in customer_agent.function_map
    
    def test_list_customers(self, customer_agent):
        """Test listing available customers."""
        response = customer_agent.list_customers()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should indicate successful retrieval of customers
        assert "רשימת הלקוחות" in response or "customer list" in response.lower()
    
    def test_create_customer(self, customer_agent):
        """Test creating a new customer."""
        # Generate a unique email
        email = self.generate_unique_email()
        first_name = "Test"
        last_name = f"Customer{random.randint(1000, 9999)}"
        
        response = customer_agent.create_customer({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "username": email,
            "password": "TestP@ssw0rd",
            "billing": {
                "first_name": first_name,
                "last_name": last_name,
                "company": "Test Company",
                "address_1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postcode": "12345",
                "country": "IL",
                "email": email,
                "phone": "555-1234-5678"
            },
            "shipping": {
                "first_name": first_name,
                "last_name": last_name,
                "company": "Test Company",
                "address_1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postcode": "12345",
                "country": "IL"
            }
        })
        
        # Check for success message
        assert "הלקוח נוצר בהצלחה" in response or "customer created successfully" in response.lower()
        
        # Extract customer ID from the response for cleanup
        import re
        id_match = re.search(r'#(\d+)', response)
        if id_match:
            customer_id = id_match.group(1)
            self.created_customers.append(customer_id)
            logger.info(f"Created test customer with ID: {customer_id}")
    
    def test_get_customer_by_id(self, customer_agent):
        """Test retrieving customer information by ID."""
        # First, create a customer to retrieve
        email = self.generate_unique_email()
        first_name = "Test"
        last_name = f"Retrieval{random.randint(1000, 9999)}"
        
        create_response = customer_agent.create_customer({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "username": email,
            "password": "TestP@ssw0rd"
        })
        
        # Extract the customer ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a customer for testing get_customer_by_id")
            
        customer_id = id_match.group(1)
        self.created_customers.append(customer_id)
        
        # Now retrieve the customer by ID
        response = customer_agent.get_customer_by_id(customer_id)
        
        # Verify the customer details are returned
        assert email in response
        assert first_name in response
        assert last_name in response
    
    def test_update_customer(self, customer_agent):
        """Test updating an existing customer."""
        # First, create a customer to update
        email = self.generate_unique_email()
        first_name = "UpdateTest"
        last_name = f"Customer{random.randint(1000, 9999)}"
        
        create_response = customer_agent.create_customer({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "username": email,
            "password": "TestP@ssw0rd"
        })
        
        # Extract the customer ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a customer for testing update_customer")
            
        customer_id = id_match.group(1)
        self.created_customers.append(customer_id)
        
        # Update the customer
        new_first_name = "UpdatedFirst"
        new_last_name = "UpdatedLast"
        update_response = customer_agent.update_customer(customer_id, {
            "first_name": new_first_name,
            "last_name": new_last_name
        })
        
        # Verify the update was successful
        assert "הלקוח עודכן בהצלחה" in update_response or "customer updated successfully" in update_response.lower()
        
        # Optional: Verify the update by getting the customer again
        get_response = customer_agent.get_customer_by_id(customer_id)
        assert new_first_name in get_response
        assert new_last_name in get_response
    
    def test_search_customers(self, customer_agent):
        """Test searching for customers."""
        # Create a customer with a searchable name
        unique_last_name = f"Searchable{random.randint(10000, 99999)}"
        email = self.generate_unique_email()
        
        create_response = customer_agent.create_customer({
            "email": email,
            "first_name": "SearchTest",
            "last_name": unique_last_name,
            "username": email,
            "password": "TestP@ssw0rd"
        })
        
        # Extract the customer ID for cleanup
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if id_match:
            self.created_customers.append(id_match.group(1))
        
        # Give the system a moment to index the new customer
        time.sleep(1)
        
        # Search for the customer using the unique last name
        search_response = customer_agent.search_customers(unique_last_name)
        
        # Verify the search found our customer
        assert unique_last_name in search_response
        assert email in search_response
    
    def test_delete_customer(self, customer_agent):
        """Test deleting a customer."""
        # First, create a customer to delete
        email = self.generate_unique_email()
        
        create_response = customer_agent.create_customer({
            "email": email,
            "first_name": "Delete",
            "last_name": "Test",
            "username": email,
            "password": "TestP@ssw0rd"
        })
        
        # Extract the customer ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a customer for testing delete_customer")
            
        customer_id = id_match.group(1)
        
        # Delete the customer
        delete_response = customer_agent.delete_customer(customer_id)
        
        # Verify deletion was successful
        assert "הלקוח נמחק בהצלחה" in delete_response or "customer deleted successfully" in delete_response.lower()
        
        # Remove from our tracking list since we've already deleted it
        if customer_id in self.created_customers:
            self.created_customers.remove(customer_id)
    
    def test_get_customer_orders(self, customer_agent):
        """Test retrieving orders for a specific customer."""
        # This test might be challenging to fully automate unless we create both a customer and order
        # For simplicity, we'll just verify the function exists and returns some response
        
        # Create a customer first
        email = self.generate_unique_email()
        create_response = customer_agent.create_customer({
            "email": email,
            "first_name": "OrderTest",
            "last_name": "Customer",
            "username": email,
            "password": "TestP@ssw0rd"
        })
        
        # Extract the customer ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a customer for testing get_customer_orders")
            
        customer_id = id_match.group(1)
        self.created_customers.append(customer_id)
        
        # Try to get the customer's orders (may be empty for a new customer)
        response = None
        try:
            response = customer_agent.get_customer_orders(customer_id)
        except Exception as e:
            # If the method doesn't exist, this would be a test failure
            pytest.fail(f"get_customer_orders method failed: {str(e)}")
        
        # Verify we got some kind of response
        assert response is not None
        
        # Even if there are no orders, there should be some meaningful response
        assert "הזמנות" in response or "orders" in response.lower() or "no orders" in response.lower() or "אין הזמנות" in response 