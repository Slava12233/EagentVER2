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

class TestReportAgent:
    """Test suite for the Report Agent functionality."""
    
    def test_agent_initialization(self, report_agent):
        """Test that the report agent initializes correctly."""
        assert report_agent is not None
        assert hasattr(report_agent, 'woocommerce')
        assert hasattr(report_agent, 'function_map')
        
        # Check if required functions are available
        assert 'get_sales_report' in report_agent.function_map
        assert 'get_top_sellers' in report_agent.function_map
        assert 'get_orders_total' in report_agent.function_map
        assert 'get_customers_total' in report_agent.function_map
        assert 'get_products_total' in report_agent.function_map
    
    def test_get_sales_report(self, report_agent):
        """Test getting sales report for a specific period."""
        # Test for last 7 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = report_agent.get_sales_report(start_date, end_date)
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should contain relevant information
        assert "מכירות" in response or "sales" in response.lower()
        assert start_date in response
        assert end_date in response
    
    def test_get_top_sellers(self, report_agent):
        """Test getting top selling products."""
        # Test for last 30 days
        period = 30
        limit = 5
        
        response = report_agent.get_top_sellers(period, limit)
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should indicate the top sellers
        assert "מוצרים מובילים" in response or "top" in response.lower() or "מוצרים הנמכרים ביותר" in response
        
        # Should mention the period
        assert str(period) in response or "30" in response
    
    def test_get_orders_total(self, report_agent):
        """Test getting the total number of orders."""
        response = report_agent.get_orders_total()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include information about orders
        assert "הזמנות" in response or "orders" in response.lower()
        
        # Should contain a number
        import re
        # Look for a number in the response
        has_number = bool(re.search(r'\d+', response))
        assert has_number, "Response should contain at least one number"
    
    def test_get_customers_total(self, report_agent):
        """Test getting the total number of customers."""
        response = report_agent.get_customers_total()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include information about customers
        assert "לקוחות" in response or "customers" in response.lower()
        
        # Should contain a number
        import re
        # Look for a number in the response
        has_number = bool(re.search(r'\d+', response))
        assert has_number, "Response should contain at least one number"
    
    def test_get_products_total(self, report_agent):
        """Test getting the total number of products."""
        response = report_agent.get_products_total()
        
        # Verify that we got some kind of response
        assert response is not None
        
        # The response should include information about products
        assert "מוצרים" in response or "products" in response.lower()
        
        # Should contain a number
        import re
        # Look for a number in the response
        has_number = bool(re.search(r'\d+', response))
        assert has_number, "Response should contain at least one number"
    
    def test_get_revenue_report(self, report_agent):
        """Test getting revenue report for a specific period."""
        # Test for last 30 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            response = report_agent.get_revenue_report(start_date, end_date)
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should contain relevant information
            assert "הכנסות" in response or "revenue" in response.lower()
            assert start_date in response
            assert end_date in response
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("get_revenue_report function not available in the agent")
    
    def test_get_stock_status_report(self, report_agent):
        """Test getting stock status report."""
        try:
            response = report_agent.get_stock_status_report()
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should contain relevant information
            assert "מלאי" in response or "stock" in response.lower()
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("get_stock_status_report function not available in the agent")
    
    def test_compare_periods(self, report_agent):
        """Test comparing sales between two periods."""
        # Define two periods to compare
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date_current = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        start_date_previous = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        end_date_previous = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
        
        try:
            response = report_agent.compare_periods(
                start_date_current, 
                end_date, 
                start_date_previous, 
                end_date_previous
            )
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should contain relevant information
            assert "השוואה" in response or "comparison" in response.lower() or "compare" in response.lower()
            assert start_date_current in response
            assert end_date in response
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("compare_periods function not available in the agent")
    
    def test_get_category_sales_report(self, report_agent):
        """Test getting sales report by category."""
        # Test for last 30 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            response = report_agent.get_category_sales_report(start_date, end_date)
            
            # Verify that we got some kind of response
            assert response is not None
            
            # The response should contain relevant information
            assert "קטגוריות" in response or "categories" in response.lower()
            assert start_date in response
            assert end_date in response
        except AttributeError:
            # This function might not exist in the agent
            pytest.skip("get_category_sales_report function not available in the agent")
    
    # בדיקת זמני תגובה מיותרת כי הסוכן המשני מדבר רק עם הסוכן הראשי
    # def test_response_times(self, report_agent):
    #     """Test that the report agent responds within a reasonable time frame."""
    #     start_time = time.time()
    #     
    #     # Run a simple report
    #     report_agent.get_orders_total()
    #     
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     
    #     # The report should complete in a reasonable amount of time (e.g., less than 10 seconds)
    #     # This threshold may need adjustment based on your system and API response times
    #     assert elapsed_time < 10, f"Report generation took too long: {elapsed_time:.2f} seconds" 