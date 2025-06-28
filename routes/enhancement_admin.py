"""
Enhancement Administration Routes
Admin interface for monitoring and managing codebase enhancements
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import json
import logging

# Import our enhancement systems
try:
    from utils.codebase_enhancer import enhancer, run_enhancement_analysis, apply_safe_enhancements
except ImportError:
    enhancer = None

try:
    from utils.intelligent_caching import cache, get_cache_health
except ImportError:
    cache = None

try:
    from utils.standardized_responses import success_response, error_response, handle_exceptions
except ImportError:
    def success_response(data=None, message="Success"):
        return jsonify({"success": True, "data": data, "message": message})
    def error_response(message="Error", status_code=400):
        return jsonify({"success": False, "message": message}), status_code
    def handle_exceptions(func):
        return func

logger = logging.getLogger(__name__)

enhancement_admin_bp = Blueprint('enhancement_admin', __name__, url_prefix='/admin/enhancements')

@enhancement_admin_bp.route('/')
def enhancement_dashboard():
    """Main enhancement dashboard"""
    try:
        # Get system health information
        system_health = {
            "cache_system": cache is not None,
            "enhancement_system": enhancer is not None,
            "monitoring_active": True,
            "last_analysis": datetime.now().isoformat()
        }
        
        # Get quick stats if systems are available
        stats = {}
        if cache:
            cache_health = get_cache_health()
            stats["cache"] = cache_health
        
        if enhancer:
            # Run quick analysis
            opportunities = enhancer.assess_and_prioritize()
            stats["enhancement_opportunities"] = len(opportunities)
            stats["high_priority"] = len([o for o in opportunities if o.priority == "high"])
        
        return render_template('admin/enhancement_dashboard.html', 
                             system_health=system_health, 
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Error loading enhancement dashboard: {e}")
        return render_template('admin/enhancement_dashboard.html', 
                             system_health={"error": str(e)}, 
                             stats={})

@enhancement_admin_bp.route('/api/analysis', methods=['GET'])
@handle_exceptions
def get_enhancement_analysis():
    """Get complete enhancement analysis"""
    if not enhancer:
        return error_response("Enhancement system not available", 503)
    
    try:
        analysis_report = run_enhancement_analysis()
        return success_response(analysis_report, "Enhancement analysis completed")
    
    except Exception as e:
        logger.error(f"Enhancement analysis failed: {e}")
        return error_response(f"Analysis failed: {str(e)}", 500)

@enhancement_admin_bp.route('/api/opportunities', methods=['GET'])
@handle_exceptions
def get_enhancement_opportunities():
    """Get enhancement opportunities with filtering"""
    if not enhancer:
        return error_response("Enhancement system not available", 503)
    
    # Get filter parameters
    category = request.args.get('category')
    priority = request.args.get('priority')
    limit = int(request.args.get('limit', 50))
    
    try:
        opportunities = enhancer.assess_and_prioritize()
        
        # Apply filters
        if category:
            opportunities = [o for o in opportunities if o.category == category]
        
        if priority:
            opportunities = [o for o in opportunities if o.priority == priority]
        
        # Limit results
        opportunities = opportunities[:limit]
        
        # Convert to dict for JSON response
        opportunities_dict = []
        for opp in opportunities:
            opportunities_dict.append({
                "category": opp.category,
                "priority": opp.priority,
                "description": opp.description,
                "file_path": opp.file_path,
                "line_number": opp.line_number,
                "estimated_effort": opp.estimated_effort,
                "potential_impact": opp.potential_impact,
                "suggested_action": opp.suggested_action
            })
        
        return success_response(opportunities_dict, f"Found {len(opportunities_dict)} opportunities")
    
    except Exception as e:
        logger.error(f"Failed to get opportunities: {e}")
        return error_response(f"Failed to get opportunities: {str(e)}", 500)

@enhancement_admin_bp.route('/api/apply-fixes', methods=['POST'])
@handle_exceptions
def apply_automatic_fixes():
    """Apply automatic fixes safely"""
    if not enhancer:
        return error_response("Enhancement system not available", 503)
    
    try:
        max_fixes = int(request.json.get('max_fixes', 5))
        
        if max_fixes > 10:
            return error_response("Maximum 10 fixes can be applied at once", 400)
        
        fixes_result = apply_safe_enhancements()
        return success_response(fixes_result, "Automatic fixes applied successfully")
    
    except Exception as e:
        logger.error(f"Failed to apply fixes: {e}")
        return error_response(f"Failed to apply fixes: {str(e)}", 500)

@enhancement_admin_bp.route('/api/cache/stats', methods=['GET'])
@handle_exceptions
def get_cache_stats():
    """Get cache system statistics"""
    if not cache:
        return error_response("Cache system not available", 503)
    
    try:
        cache_stats = cache.get_stats()
        cache_health = get_cache_health()
        
        return success_response({
            "statistics": cache_stats,
            "health": cache_health
        }, "Cache statistics retrieved")
    
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return error_response(f"Failed to get cache stats: {str(e)}", 500)

@enhancement_admin_bp.route('/api/cache/clear', methods=['POST'])
@handle_exceptions
def clear_cache():
    """Clear cache system"""
    if not cache:
        return error_response("Cache system not available", 503)
    
    try:
        cache.clear()
        return success_response(None, "Cache cleared successfully")
    
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return error_response(f"Failed to clear cache: {str(e)}", 500)

@enhancement_admin_bp.route('/api/system-health', methods=['GET'])
@handle_exceptions
def get_system_health():
    """Get overall system health"""
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "cache": {
                "available": cache is not None,
                "status": "healthy" if cache else "unavailable"
            },
            "enhancer": {
                "available": enhancer is not None,
                "status": "healthy" if enhancer else "unavailable"
            },
            "database": {
                "available": True,  # Assume available if we can run this route
                "status": "healthy"
            }
        }
    }
    
    # Add detailed health if systems are available
    if cache:
        try:
            cache_health = get_cache_health()
            health_data["systems"]["cache"]["details"] = cache_health
        except Exception as e:
            health_data["systems"]["cache"]["error"] = str(e)
    
    overall_status = "healthy"
    if any(s["status"] != "healthy" for s in health_data["systems"].values()):
        overall_status = "degraded"
    
    health_data["overall_status"] = overall_status
    
    return success_response(health_data, f"System is {overall_status}")

@enhancement_admin_bp.route('/api/file-analysis/<path:file_path>', methods=['GET'])
@handle_exceptions
def get_file_analysis(file_path):
    """Get detailed analysis for a specific file"""
    if not enhancer:
        return error_response("Enhancement system not available", 503)
    
    try:
        if file_path in enhancer.analysis_results:
            analysis = enhancer.analysis_results[file_path]
            
            analysis_dict = {
                "file_path": analysis.file_path,
                "total_lines": analysis.total_lines,
                "function_count": analysis.function_count,
                "class_count": analysis.class_count,
                "imports": analysis.imports,
                "potential_issues": analysis.potential_issues,
                "optimization_opportunities": analysis.optimization_opportunities,
                "complexity_score": analysis.complexity_score
            }
            
            return success_response(analysis_dict, f"Analysis for {file_path}")
        else:
            return error_response(f"No analysis found for {file_path}", 404)
    
    except Exception as e:
        logger.error(f"Failed to get file analysis: {e}")
        return error_response(f"Failed to get file analysis: {str(e)}", 500)

@enhancement_admin_bp.route('/api/generate-report', methods=['POST'])
@handle_exceptions
def generate_enhancement_report():
    """Generate and save enhancement report"""
    if not enhancer:
        return error_response("Enhancement system not available", 503)
    
    try:
        report = run_enhancement_analysis()
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"logs/enhancement_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return success_response({
            "report": report,
            "saved_to": report_path
        }, "Enhancement report generated successfully")
    
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return error_response(f"Failed to generate report: {str(e)}", 500)

# Error handlers for the blueprint
@enhancement_admin_bp.errorhandler(404)
def not_found(error):
    return error_response("Enhancement endpoint not found", 404)

@enhancement_admin_bp.errorhandler(500)
def internal_error(error):
    return error_response("Internal enhancement system error", 500)