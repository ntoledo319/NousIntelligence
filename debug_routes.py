import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""Debug route registration issues"""

import sys
from app_working import app

def debug_routes():
    """Debug route registration"""
    logger.info(🔍 Debugging NOUS Route Registration)
    logger.info(=)
    
    with app.app_context():
        logger.info(📊 Total registered blueprints: {len(app.blueprints)})
        
        for name, blueprint in app.blueprints.items():
            logger.info(✅ Blueprint: {name})
        
        logger.info(\n🛣️  All registered routes:)
        for rule in app.url_map.iter_rules():
            logger.info(  {rule.rule} → {rule.endpoint} ({rule.methods}))
        
        logger.info(\n🔍 Looking for index/demo routes:)
        demo_routes = [rule for rule in app.url_map.iter_rules() if 'demo' in rule.rule]
        if demo_routes:
            for route in demo_routes:
                logger.info(  ✅ {route.rule} → {route.endpoint})
        else:
            logger.info(  ❌ No demo routes found)
        
        logger.info(\n🔍 Checking index blueprint specifically:)
        if 'index' in app.blueprints:
            logger.info(  ✅ Index blueprint is registered)
        else:
            logger.info(  ❌ Index blueprint not registered)

if __name__ == "__main__":
    debug_routes()