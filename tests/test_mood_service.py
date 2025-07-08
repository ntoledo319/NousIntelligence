import pytest
from unittest.mock import Mock, patch
from tests.base_test import BaseTestCase
from src.application.services.mood_service import MoodService
from src.infrastructure.error_handling import ValidationError, NotFoundError

class TestMoodService(BaseTestCase):
    """Test mood service"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository"""
        return MoodService(mock_repository)
    
    def test_get_all_success(self, service, mock_repository):
        """Test successful get all"""
        # Arrange
        expected = [{'id': '1', 'name': 'test mood'}]
        mock_repository.find_by_user.return_value = expected
        user_id = 'user123'
        
        # Act
        result = service.get_all(user_id)
        
        # Assert
        assert result == expected
        mock_repository.find_by_user.assert_called_once_with(user_id)
    
    def test_get_by_id_success(self, service, mock_repository):
        """Test successful get by ID"""
        # Arrange
        expected = {'id': '1', 'name': 'test mood'}
        mock_repository.find_by_id_and_user.return_value = expected
        user_id = 'user123'
        item_id = '1'
        
        # Act
        result = service.get_by_id(item_id, user_id)
        
        # Assert
        assert result == expected
        mock_repository.find_by_id_and_user.assert_called_once_with(item_id, user_id)
    
    def test_get_by_id_not_found(self, service, mock_repository):
        """Test get by ID when not found"""
        # Arrange
        mock_repository.find_by_id_and_user.return_value = None
        
        # Act
        result = service.get_by_id('nonexistent', 'user123')
        
        # Assert
        assert result is None
    
    def test_create_success(self, service, mock_repository):
        """Test successful creation"""
        # Arrange
        data = {'name': 'New mood'}
        expected = {'id': '1', 'name': 'New mood', 'user_id': 'user123'}
        mock_repository.create.return_value = expected
        user_id = 'user123'
        
        # Act
        result = service.create(data, user_id)
        
        # Assert
        assert result == expected
        assert mock_repository.create.call_args[0][0]['user_id'] == user_id
    
    def test_update_success(self, service, mock_repository):
        """Test successful update"""
        # Arrange
        data = {'name': 'Updated mood'}
        expected = {'id': '1', 'name': 'Updated mood'}
        mock_repository.update.return_value = expected
        
        # Act
        result = service.update('1', data, 'user123')
        
        # Assert
        assert result == expected
        mock_repository.update.assert_called_once_with('1', data, 'user123')
    
    def test_delete_success(self, service, mock_repository):
        """Test successful deletion"""
        # Arrange
        mock_repository.delete.return_value = True
        
        # Act
        result = service.delete('1', 'user123')
        
        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with('1', 'user123')
    
    def test_repository_error_handling(self, service, mock_repository):
        """Test error handling when repository fails"""
        # Arrange
        mock_repository.find_by_user.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            service.get_all('user123')
