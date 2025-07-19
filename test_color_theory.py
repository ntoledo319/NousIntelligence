import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Color Theory Enhancement Validation
Tests that the enhanced CSS color scheme is properly applied
"""

import requests
import re

def test_color_theory_enhancements():
    """Test that color theory improvements are applied to the landing page"""
    try:
        # Test the landing page
        response = requests.get("http://localhost:8080/", timeout=10)
        html_content = response.text
        
        # Check for enhanced CSS file references
        css_references = re.findall(r'href="[^"]*\.css[^"]*"', html_content)
        logger.info("CSS files referenced: {}".format(len(css_references)))
        
        # Check for key color theory elements in HTML structure
        hero_section = "hero" in html_content
        features_section = "features" in html_content
        cta_section = "cta" in html_content
        
        logger.info("Hero section: {}".format('Present' if hero_section else 'Missing'))
        logger.info("Features section: {}".format('Present' if features_section else 'Missing'))
        logger.info("CTA section: {}".format('Present' if cta_section else 'Missing'))
        
        # Check for enhanced button classes
        primary_button = 'class="google-signin-btn primary"' in html_content
        secondary_button = 'class="google-signin-btn secondary"' in html_content
        
        logger.info("Primary button: {}".format('Present' if primary_button else 'Missing'))
        logger.info("Secondary button: {}".format('Present' if secondary_button else 'Missing'))
        
        # Check for color variables in CSS
        css_urls = [match.group(1) for match in re.finditer(r'href="([^"]*\.css)"', html_content)]
        color_vars_found = False
        
        for css_url in css_urls:
            if not css_url.startswith(('http', '//')):
                css_url = "http://localhost:8080{}{}".format(
                    '' if css_url.startswith('/') else '/',
                    css_url
                )
            
            try:
                css_response = requests.get(css_url, timeout=10)
                if css_response.status_code == 200:
                    css_content = css_response.text
                    if '--primary-color:' in css_content and '--secondary-color:' in css_content:
                        color_vars_found = True
                        break
            except Exception as e:
                logger.warning("Could not fetch CSS file {}: {}".format(css_url, str(e)))
        
        logger.info("CSS color variables: {}".format('Found' if color_vars_found else 'Missing'))
        
        # Check for accessibility features
        alt_text = 'alt=' in html_content
        aria_labels = 'aria-label=' in html_content
        
        logger.info("Alt text: {}".format('Present' if alt_text else 'Missing'))
        logger.info("ARIA labels: {}".format('Present' if aria_labels else 'Missing'))
        
        # Check for responsive design meta tag
        viewport_meta = 'name="viewport"' in html_content
        logger.info("Viewport meta tag: {}".format('Present' if viewport_meta else 'Missing'))
        
        # Check for modern CSS features
        css_grid = 'display: grid' in html_content or 'display:grid' in html_content
        flexbox = 'display: flex' in html_content or 'display:flex' in html_content
        
        logger.info("CSS Grid usage: {}".format('Present' if css_grid else 'Missing'))
        logger.info("Flexbox usage: {}".format('Present' if flexbox else 'Missing'))
        
        # Overall assessment
        all_checks = [
            hero_section,
            features_section,
            cta_section,
            primary_button,
            color_vars_found,
            alt_text,
            viewport_meta,
            css_grid or flexbox
        ]
        
        overall_score = sum(1 for check in all_checks if check) / len(all_checks) * 100
        
        if overall_score >= 90:
            logger.info("Color theory implementation: EXCELLENT ({:.1f}%)".format(overall_score))
        elif overall_score >= 70:
            logger.info("Color theory implementation: GOOD ({:.1f}%)".format(overall_score))
        else:
            logger.info("Color theory implementation: NEEDS IMPROVEMENT ({:.1f}%)".format(overall_score))
        
        return overall_score >= 70
        
    except Exception as e:
        logger.error("Error testing color theory: {}".format(str(e)))
        return False

if __name__ == "__main__":
    logger.info("Testing Color Theory Enhancements...\n")
    success = test_color_theory_enhancements()
    logger.info("\n" + "="*50)
    logger.info("Test {}".format('PASSED' if success else 'FAILED'))