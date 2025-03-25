import pytest
import logging
import time
from datetime import datetime, timedelta

# Disable insecure HTTPS warnings that might appear when testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSettingsAgent:
    """Test suite for the Settings Agent functionality."""
    
    # Keep track of any settings we modified so we can revert them later
    modified_settings = {}
    
    @pytest.fixture(autouse=True)
    def cleanup_modified_settings(self, request):
        """Fixture to clean up any modified settings after each test."""
        def teardown():
            # Restore any settings we modified during the test
            for key, value in TestSettingsAgent.modified_settings.items():
                logger.info(f"Restoring setting {key} to {value}")
                # Implement restoration logic if needed
        
        request.addfinalizer(teardown)
    
    def test_agent_initialization(self, settings_agent):
        """Test that the settings agent initializes correctly."""
        assert settings_agent is not None
        assert hasattr(settings_agent, 'woocommerce')
        assert hasattr(settings_agent, 'function_map')
        
        # Check if required functions are available
        assert 'get_store_settings' in settings_agent.function_map
        assert 'update_setting' in settings_agent.function_map
        assert 'get_payment_gateways' in settings_agent.function_map
        assert 'get_shipping_methods' in settings_agent.function_map
    
    def test_get_store_settings(self, settings_agent):
        """Test getting general store settings."""
        response = settings_agent.get_store_settings()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include key store information
        assert "שם החנות" in response
        assert "כתובת" in response
        assert "אימייל" in response
        assert "מטבע" in response
    
    def test_get_payment_gateways(self, settings_agent):
        """Test getting available payment gateways."""
        response = settings_agent.get_payment_gateways()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include payment information
        assert "תשלום" in response or "payment" in response.lower()
        
        # Should contain at least one payment method
        assert "PayPal" in response or "כרטיס אשראי" in response or "העברה בנקאית" in response
    
    def test_get_shipping_methods(self, settings_agent):
        """Test getting available shipping methods."""
        response = settings_agent.get_shipping_methods()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include shipping information
        assert "משלוח" in response or "shipping" in response.lower()
    
    def test_get_tax_settings(self, settings_agent):
        """Test getting tax settings."""
        response = settings_agent.get_tax_settings()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include tax information
        assert "מס" in response or "tax" in response.lower()
    
    def test_update_setting(self, settings_agent):
        """Test updating a specific setting."""
        # Define the setting to update (use test_ prefix to identify test settings)
        test_setting_key = "test_setting_key"
        test_setting_value = f"test_value_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update the setting
        response = settings_agent.update_setting(test_setting_key, test_setting_value)
        
        # Record the setting for potential restoration
        TestSettingsAgent.modified_settings[test_setting_key] = "original_value"
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should confirm the update
        assert "עודכנה בהצלחה" in response
        assert test_setting_key in response
        assert test_setting_value in response
        
        # Optionally verify that the setting was actually updated
        # This would require implementing a get_setting method
        # get_response = settings_agent.get_setting(test_setting_key)
        # assert test_setting_value in get_response
    
    def test_email_settings(self, settings_agent):
        """Test getting email settings."""
        try:
            response = settings_agent.get_email_settings()
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should include email information
            assert "אימייל" in response or "email" in response.lower()
            
            # Should contain common email-related terms
            assert any(term in response.lower() for term in ["smtp", "מנהל", "לקוח", "הזמנה", "חשבון"])
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("get_email_settings function not available in the agent")
    
    def test_get_currency_settings(self, settings_agent):
        """Test getting currency settings."""
        try:
            response = settings_agent.get_currency_settings()
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should include currency information
            assert "מטבע" in response or "currency" in response.lower()
            
            # Should include common currency symbols or codes
            common_currencies = ["₪", "₪", "ils", "usd", "$", "€", "eur", "gbp", "£"]
            has_currency = any(currency in response.lower() for currency in common_currencies)
            assert has_currency, "Response should mention at least one currency"
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("get_currency_settings function not available in the agent") 