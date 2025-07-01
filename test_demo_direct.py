import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""Test demo route directly to see the error"""

from app_working import app

def test_demo_route():
    """Test demo route directly"""
    with app.test_client() as client:
        with app.app_context():
            logger.info(Testing demo route directly...)
            try:
                response = client.get('/demo')
                logger.info(Status Code: {response.status_code})
                if response.status_code != 200:
                    logger.info(Response data: {response.data.decode()})
                else:
                    logger.info(Demo route working correctly!)
                    logger.info(Response length: {len(response.data)} bytes)
                    
            except Exception as e:
                logger.error(Error testing demo route: {e})
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_demo_route()