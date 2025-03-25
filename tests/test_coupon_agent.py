import pytest
import time
import logging
import random
import string
from datetime import datetime, timedelta

# Disable insecure HTTPS warnings that might appear when testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCouponAgent:
    """Test suite for the Coupon Agent functionality."""
    
    created_coupons = []  # Track coupons created during tests for cleanup
    
    @pytest.fixture(autouse=True)
    def cleanup_created_coupons(self, request):
        """Fixture to clean up any coupons created during tests."""
        yield
        
        # Skip cleanup if there's nothing to clean
        if not self.created_coupons:
            return
            
        logger.info(f"Cleaning up {len(self.created_coupons)} coupons created during tests")
        for coupon_id in self.created_coupons:
            try:
                response = request.getfixturevalue("coupon_agent").delete_coupon(coupon_id)
                if "הקופון נמחק בהצלחה" in response or "successfully deleted" in response.lower():
                    logger.info(f"Cleaned up coupon ID: {coupon_id}")
                else:
                    logger.warning(f"Failed to clean up coupon ID: {coupon_id}. Response: {response}")
            except Exception as e:
                logger.error(f"Error cleaning up coupon ID {coupon_id}: {str(e)}")
        
        # Clear the list after cleanup attempt
        self.created_coupons.clear()
    
    def generate_unique_coupon_code(self):
        """Generate a unique coupon code for testing."""
        timestamp = int(time.time())
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"TEST{timestamp}{random_chars}"
    
    def test_agent_initialization(self, coupon_agent):
        """Test that the coupon agent initializes correctly."""
        assert coupon_agent is not None
        assert hasattr(coupon_agent, 'woocommerce')
        assert hasattr(coupon_agent, 'function_map')
        
        # Check if required functions are available
        assert 'list_coupons' in coupon_agent.function_map
        assert 'create_coupon' in coupon_agent.function_map
        assert 'get_coupon_by_id' in coupon_agent.function_map
        assert 'update_coupon' in coupon_agent.function_map
        assert 'delete_coupon' in coupon_agent.function_map
        assert 'search_coupons' in coupon_agent.function_map
    
    def test_list_coupons(self, coupon_agent):
        """Test listing available coupons."""
        response = coupon_agent.list_coupons()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should indicate successful retrieval of coupons
        assert "רשימת הקופונים" in response or "coupon list" in response.lower()
    
    def test_create_coupon(self, coupon_agent):
        """Test creating a new coupon."""
        # Generate a unique coupon code
        code = self.generate_unique_coupon_code()
        
        # Create a coupon that expires in 7 days
        expiry_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = coupon_agent.create_coupon({
            "code": code,
            "discount_type": "percent",
            "amount": "10",
            "individual_use": True,
            "exclude_sale_items": True,
            "minimum_amount": "100",
            "maximum_amount": "1000",
            "usage_limit": 5,
            "expiry_date": expiry_date
        })
        
        # Check for success message
        assert "הקופון נוצר בהצלחה" in response or "coupon created successfully" in response.lower()
        
        # Extract coupon ID from the response for cleanup
        # Typical success message formats: "הקופון {code} (#{id}) נוצר בהצלחה"
        import re
        id_match = re.search(r'#(\d+)', response)
        if id_match:
            coupon_id = id_match.group(1)
            self.created_coupons.append(coupon_id)
            logger.info(f"Created test coupon with ID: {coupon_id}")
    
    def test_get_coupon_by_id(self, coupon_agent):
        """Test retrieving coupon information by ID."""
        # First, create a coupon to retrieve
        code = self.generate_unique_coupon_code()
        create_response = coupon_agent.create_coupon({
            "code": code,
            "discount_type": "percent",
            "amount": "15"
        })
        
        # Extract the coupon ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a coupon for testing get_coupon_by_id")
            
        coupon_id = id_match.group(1)
        self.created_coupons.append(coupon_id)
        
        # Now retrieve the coupon by ID
        response = coupon_agent.get_coupon_by_id(coupon_id)
        
        # Verify the coupon details are returned
        assert code in response
        assert "15" in response  # The amount we set
    
    def test_update_coupon(self, coupon_agent):
        """Test updating an existing coupon."""
        # First, create a coupon to update
        code = self.generate_unique_coupon_code()
        create_response = coupon_agent.create_coupon({
            "code": code,
            "discount_type": "percent",
            "amount": "20"
        })
        
        # Extract the coupon ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a coupon for testing update_coupon")
            
        coupon_id = id_match.group(1)
        self.created_coupons.append(coupon_id)
        
        # Update the coupon
        new_amount = "25"
        update_response = coupon_agent.update_coupon(coupon_id, {
            "amount": new_amount,
            "description": "Updated test coupon"
        })
        
        # Verify the update was successful
        assert "הקופון עודכן בהצלחה" in update_response or "coupon updated successfully" in update_response.lower()
        
        # Optional: Verify the update by getting the coupon again
        get_response = coupon_agent.get_coupon_by_id(coupon_id)
        assert new_amount in get_response
        assert "Updated test coupon" in get_response
    
    def test_search_coupons(self, coupon_agent):
        """Test searching for coupons."""
        # Create a coupon with a searchable prefix
        search_prefix = "SEARCHABLE"
        code = f"{search_prefix}{self.generate_unique_coupon_code()}"
        
        create_response = coupon_agent.create_coupon({
            "code": code,
            "discount_type": "percent",
            "amount": "30"
        })
        
        # Extract the coupon ID for cleanup
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if id_match:
            self.created_coupons.append(id_match.group(1))
        
        # Give the system a moment to index the new coupon
        time.sleep(1)
        
        # Search for the coupon using the prefix
        search_response = coupon_agent.search_coupons(search_prefix)
        
        # Verify the search found our coupon
        assert code in search_response
    
    def test_delete_coupon(self, coupon_agent):
        """Test deleting a coupon."""
        # First, create a coupon to delete
        code = self.generate_unique_coupon_code()
        create_response = coupon_agent.create_coupon({
            "code": code,
            "discount_type": "percent",
            "amount": "5"
        })
        
        # Extract the coupon ID
        import re
        id_match = re.search(r'#(\d+)', create_response)
        if not id_match:
            pytest.skip("Could not create a coupon for testing delete_coupon")
            
        coupon_id = id_match.group(1)
        
        # Delete the coupon
        delete_response = coupon_agent.delete_coupon(coupon_id)
        
        # Verify deletion was successful
        assert "הקופון נמחק בהצלחה" in delete_response or "coupon deleted successfully" in delete_response.lower()
        
        # Remove from our tracking list since we've already deleted it
        if coupon_id in self.created_coupons:
            self.created_coupons.remove(coupon_id) 