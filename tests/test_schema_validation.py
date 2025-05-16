"""
Unit tests for the schema validation module

These tests verify the functionality of schema validation features including:
- Schema registration and retrieval
- Data validation against schemas
- Request validation
- Decorator functionality

@module: test_schema_validation
@author: NOUS Development Team
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from flask import Flask, request, jsonify

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.schema_validation import (
    register_schema,
    get_schema,
    validate_data,
    validate_request,
    validate_with_schema,
    SCHEMA_REGISTRY,
    string_schema,
    email_schema,
    number_schema,
    boolean_schema,
    array_schema,
    object_schema
)

class TestSchemaRegistry(unittest.TestCase):
    """Test cases for schema registry functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear registry before each test
        SCHEMA_REGISTRY.clear()
    
    def test_register_schema(self):
        """Test registering a schema"""
        test_schema = {"type": "string"}
        register_schema("test_schema", test_schema)
        
        # Check schema is in registry
        self.assertIn("test_schema", SCHEMA_REGISTRY)
        self.assertEqual(SCHEMA_REGISTRY["test_schema"], test_schema)
    
    def test_register_duplicate_schema(self):
        """Test overwriting an existing schema"""
        register_schema("test_schema", {"type": "string"})
        register_schema("test_schema", {"type": "integer"})
        
        # Check schema was overwritten
        self.assertEqual(SCHEMA_REGISTRY["test_schema"]["type"], "integer")
    
    def test_get_schema(self):
        """Test retrieving a schema"""
        test_schema = {"type": "string"}
        register_schema("test_schema", test_schema)
        
        # Get the schema
        schema = get_schema("test_schema")
        
        # Check schema is correct
        self.assertEqual(schema, test_schema)
    
    def test_get_nonexistent_schema(self):
        """Test getting a nonexistent schema"""
        schema = get_schema("nonexistent")
        self.assertIsNone(schema)

class TestDataValidation(unittest.TestCase):
    """Test cases for data validation functionality"""
    
    def test_validate_valid_data(self):
        """Test validating data that matches schema"""
        schema = {"type": "string"}
        is_valid, error = validate_data("test string", schema)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_invalid_data(self):
        """Test validating data that doesn't match schema"""
        schema = {"type": "string"}
        is_valid, error = validate_data(123, schema)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_complex_schema(self):
        """Test validating against a complex schema"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        # Valid data
        is_valid, error = validate_data({"name": "John", "age": 30}, schema)
        self.assertTrue(is_valid)
        
        # Missing required field
        is_valid, error = validate_data({"age": 30}, schema)
        self.assertFalse(is_valid)
        
        # Invalid type
        is_valid, error = validate_data({"name": "John", "age": "thirty"}, schema)
        self.assertFalse(is_valid)

class TestRequestValidation(unittest.TestCase):
    """Test cases for request validation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
    
    def test_validate_json_request(self):
        """Test validating a JSON request"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        
        with self.app.test_request_context(
            '/test',
            method='POST',
            json={"name": "John"},
            content_type='application/json'
        ):
            is_valid, error = validate_request(request, schema)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
    
    def test_validate_invalid_json_request(self):
        """Test validating an invalid JSON request"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        
        with self.app.test_request_context(
            '/test',
            method='POST',
            json={"age": 30},  # Missing required name field
            content_type='application/json'
        ):
            is_valid, error = validate_request(request, schema)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error)
    
    def test_validate_form_request(self):
        """Test validating a form request"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        
        with self.app.test_request_context(
            '/test',
            method='POST',
            data={"name": "John"}
        ):
            is_valid, error = validate_request(request, schema)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
    
    def test_validate_unsupported_content_type(self):
        """Test validating a request with unsupported content type"""
        schema = {"type": "object"}
        
        with self.app.test_request_context(
            '/test',
            method='POST',
            headers={'Content-Type': 'text/plain'},
            data="plain text"
        ):
            is_valid, error = validate_request(request, schema)
            self.assertFalse(is_valid)
            self.assertEqual(error, "Unsupported content type")

class TestSchemaDecorator(unittest.TestCase):
    """Test cases for schema validation decorator"""
    
    def setUp(self):
        """Set up test environment"""
        SCHEMA_REGISTRY.clear()
        self.app = Flask(__name__)
        
        # Register test schema
        register_schema("test_schema", {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        })
        
        # Create test route
        @self.app.route('/test', methods=['POST'])
        @validate_with_schema("test_schema")
        def test_route():
            return jsonify({"success": True})
    
    def test_decorator_with_valid_data(self):
        """Test decorator with valid request data"""
        with self.app.test_client() as client:
            response = client.post('/test', json={"name": "John"})
            self.assertEqual(response.status_code, 200)
    
    def test_decorator_with_invalid_data(self):
        """Test decorator with invalid request data"""
        with self.app.test_client() as client:
            response = client.post('/test', json={"age": 30})  # Missing required name field
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Validation error")
    
    def test_decorator_with_nonexistent_schema(self):
        """Test decorator with nonexistent schema"""
        # Create new route with nonexistent schema
        @self.app.route('/nonexistent', methods=['POST'])
        @validate_with_schema("nonexistent_schema")
        def nonexistent_route():
            return jsonify({"success": True})
        
        with self.app.test_client() as client:
            response = client.post('/nonexistent', json={})
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Server configuration error")

class TestSchemaGenerators(unittest.TestCase):
    """Test cases for schema generator functions"""
    
    def test_string_schema(self):
        """Test string schema generator"""
        # Basic string schema
        schema = string_schema()
        self.assertEqual(schema["type"], "string")
        self.assertEqual(schema["minLength"], 1)
        
        # String schema with constraints
        schema = string_schema(min_length=5, max_length=10, pattern=r"[a-z]+")
        self.assertEqual(schema["minLength"], 5)
        self.assertEqual(schema["maxLength"], 10)
        self.assertEqual(schema["pattern"], r"[a-z]+")
    
    def test_email_schema(self):
        """Test email schema generator"""
        schema = email_schema()
        self.assertEqual(schema["type"], "string")
        self.assertEqual(schema["format"], "email")
        self.assertIn("pattern", schema)
    
    def test_number_schema(self):
        """Test number schema generator"""
        # Basic number schema
        schema = number_schema()
        self.assertEqual(schema["type"], "number")
        
        # Integer schema with constraints
        schema = number_schema(minimum=0, maximum=100, integer_only=True)
        self.assertEqual(schema["type"], "integer")
        self.assertEqual(schema["minimum"], 0)
        self.assertEqual(schema["maximum"], 100)
    
    def test_boolean_schema(self):
        """Test boolean schema generator"""
        schema = boolean_schema()
        self.assertEqual(schema["type"], "boolean")
    
    def test_array_schema(self):
        """Test array schema generator"""
        items = {"type": "string"}
        schema = array_schema(items, min_items=1, max_items=10)
        
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"], items)
        self.assertEqual(schema["minItems"], 1)
        self.assertEqual(schema["maxItems"], 10)
    
    def test_object_schema(self):
        """Test object schema generator"""
        properties = {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        }
        required = ["name"]
        
        schema = object_schema(properties, required)
        
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["properties"], properties)
        self.assertEqual(schema["required"], required)

if __name__ == '__main__':
    unittest.main() 