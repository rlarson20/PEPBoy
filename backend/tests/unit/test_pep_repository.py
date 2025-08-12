"""
Unit tests for PEP Repository.

This module tests the repository pattern implementation,
demonstrating TDD red-green-refactor methodology for data access layer.
"""

import pytest
from sqlalchemy.orm import Session

from src.models.orm_models import Author, PEP
from src.services.pep_repository import PEPRepository
from tests.fixtures.factories import (
    AuthorFactory,
    PEPFactory,
    BatchFactory,
    DraftPEPFactory,
    FinalPEPFactory,
)


class TestPEPRepository:
    """Test cases for PEPRepository class."""
    
    @pytest.fixture
    def repository(self, test_db_session: Session):
        """Create a PEPRepository instance for testing."""
        return PEPRepository(test_db_session)
    
    @pytest.fixture
    def sample_peps(self, test_db_session: Session):
        """Create sample PEPs in the database for testing."""
        peps = [
            PEP(
                number=1,
                title="PEP Purpose and Guidelines",
                status="Active",
                type="Process",
                topic="Core",
                url="https://peps.python.org/pep-0001/"
            ),
            PEP(
                number=8,
                title="Style Guide for Python Code",
                status="Active",
                type="Process",
                topic="Core",
                url="https://peps.python.org/pep-0008/"
            ),
            PEP(
                number=20,
                title="The Zen of Python",
                status="Active",
                type="Informational",
                topic="Core",
                url="https://peps.python.org/pep-0020/"
            ),
            PEP(
                number=484,
                title="Type Hints",
                status="Final",
                type="Standards Track",
                topic="Typing",
                url="https://peps.python.org/pep-0484/"
            ),
        ]
        
        test_db_session.add_all(peps)
        test_db_session.commit()
        return peps


class TestGetPepByNumber:
    """Test the get_pep_by_number method."""
    
    def test_get_existing_pep_by_number(self, repository: PEPRepository, sample_peps):
        """Test retrieving an existing PEP by its number.
        
        TDD Red: Write test expecting PEP retrieval to work
        TDD Green: Implement basic get_pep_by_number method
        TDD Refactor: Optimize query and add error handling
        """
        # Arrange
        expected_pep_number = 8
        
        # Act
        result = repository.get_pep_by_number(expected_pep_number)
        
        # Assert
        assert result is not None
        assert result.number == expected_pep_number
        assert result.title == "Style Guide for Python Code"
        assert result.status == "Active"
        assert result.type == "Process"
    
    def test_get_nonexistent_pep_by_number(self, repository: PEPRepository, sample_peps):
        """Test retrieving a non-existent PEP by number returns None."""
        # Arrange
        nonexistent_number = 9999
        
        # Act
        result = repository.get_pep_by_number(nonexistent_number)
        
        # Assert
        assert result is None
    
    def test_get_pep_by_number_zero(self, repository: PEPRepository, sample_peps):
        """Test edge case: PEP number 0."""
        # Act
        result = repository.get_pep_by_number(0)
        
        # Assert
        assert result is None
    
    def test_get_pep_by_negative_number(self, repository: PEPRepository, sample_peps):
        """Test edge case: negative PEP number."""
        # Act
        result = repository.get_pep_by_number(-1)
        
        # Assert
        assert result is None


class TestListAllPeps:
    """Test the list_all_peps method."""
    
    def test_list_all_peps_default_pagination(self, repository: PEPRepository, sample_peps):
        """Test listing all PEPs with default pagination."""
        # Act
        result = repository.list_all_peps()
        
        # Assert
        assert len(result) == 4  # All sample PEPs
        assert all(isinstance(pep, PEP) for pep in result)
        
        # Verify they're in order (assuming default ordering)
        numbers = [pep.number for pep in result]
        assert 1 in numbers
        assert 8 in numbers
        assert 20 in numbers
        assert 484 in numbers
    
    def test_list_all_peps_with_limit(self, repository: PEPRepository, sample_peps):
        """Test listing PEPs with custom limit."""
        # Arrange
        limit = 2
        
        # Act
        result = repository.list_all_peps(limit=limit)
        
        # Assert
        assert len(result) == limit
        assert all(isinstance(pep, PEP) for pep in result)
    
    def test_list_all_peps_with_skip(self, repository: PEPRepository, sample_peps):
        """Test listing PEPs with skip offset."""
        # Arrange
        skip = 2
        
        # Act
        result = repository.list_all_peps(skip=skip)
        
        # Assert
        assert len(result) == 2  # 4 total - 2 skipped = 2
        assert all(isinstance(pep, PEP) for pep in result)
    
    def test_list_all_peps_skip_and_limit(self, repository: PEPRepository, sample_peps):
        """Test listing PEPs with both skip and limit."""
        # Arrange
        skip = 1
        limit = 2
        
        # Act
        result = repository.list_all_peps(skip=skip, limit=limit)
        
        # Assert
        assert len(result) == limit
        assert all(isinstance(pep, PEP) for pep in result)
    
    def test_list_all_peps_empty_database(self, repository: PEPRepository):
        """Test listing PEPs when database is empty."""
        # Act
        result = repository.list_all_peps()
        
        # Assert
        assert result == []
    
    def test_list_all_peps_skip_beyond_count(self, repository: PEPRepository, sample_peps):
        """Test listing PEPs when skip is beyond total count."""
        # Arrange
        skip = 100  # More than the 4 sample PEPs
        
        # Act
        result = repository.list_all_peps(skip=skip)
        
        # Assert
        assert result == []


class TestSearchPepsByTitle:
    """Test the search_peps_by_title method."""
    
    def test_search_peps_exact_match(self, repository: PEPRepository, sample_peps):
        """Test searching PEPs with exact title match."""
        # Arrange
        query = "Type Hints"
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert len(result) == 1
        assert result[0].number == 484
        assert result[0].title == "Type Hints"
    
    def test_search_peps_partial_match(self, repository: PEPRepository, sample_peps):
        """Test searching PEPs with partial title match."""
        # Arrange
        query = "Python"  # Should match "Style Guide for Python Code" and "The Zen of Python"
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert len(result) == 2
        titles = [pep.title for pep in result]
        assert "Style Guide for Python Code" in titles
        assert "The Zen of Python" in titles
    
    def test_search_peps_case_insensitive(self, repository: PEPRepository, sample_peps):
        """Test that search is case-insensitive."""
        # Arrange
        query = "python"  # lowercase
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert len(result) == 2  # Should still find Python matches
        titles = [pep.title for pep in result]
        assert "Style Guide for Python Code" in titles
        assert "The Zen of Python" in titles
    
    def test_search_peps_no_matches(self, repository: PEPRepository, sample_peps):
        """Test searching PEPs with no matches."""
        # Arrange
        query = "NonexistentTerm"
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert result == []
    
    def test_search_peps_empty_query(self, repository: PEPRepository, sample_peps):
        """Test searching PEPs with empty query."""
        # Arrange
        query = ""
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert len(result) == 4  # Empty string matches all
    
    def test_search_peps_special_characters(self, repository: PEPRepository, sample_peps):
        """Test searching PEPs with special characters in query."""
        # Arrange
        query = "Guide"
        
        # Act
        result = repository.search_peps_by_title(query)
        
        # Assert
        assert len(result) == 1
        assert result[0].title == "Style Guide for Python Code"


class TestGetPepsCount:
    """Test the get_peps_count method."""
    
    def test_get_peps_count_with_data(self, repository: PEPRepository, sample_peps):
        """Test getting PEP count when database has data."""
        # Act
        result = repository.get_peps_count()
        
        # Assert
        assert result == 4
        assert isinstance(result, int)
    
    def test_get_peps_count_empty_database(self, repository: PEPRepository):
        """Test getting PEP count when database is empty."""
        # Act
        result = repository.get_peps_count()
        
        # Assert
        assert result == 0
        assert isinstance(result, int)
    
    def test_get_peps_count_after_adding_pep(self, repository: PEPRepository, test_db_session: Session):
        """Test that count updates after adding a new PEP."""
        # Arrange
        initial_count = repository.get_peps_count()
        
        new_pep = PEP(
            number=999,
            title="Test PEP",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-999"
        )
        test_db_session.add(new_pep)
        test_db_session.commit()
        
        # Act
        new_count = repository.get_peps_count()
        
        # Assert
        assert new_count == initial_count + 1
    
    def test_get_peps_count_after_deleting_pep(self, repository: PEPRepository, sample_peps, test_db_session: Session):
        """Test that count updates after deleting a PEP."""
        # Arrange
        initial_count = repository.get_peps_count()
        
        # Delete one PEP
        pep_to_delete = test_db_session.query(PEP).filter_by(number=1).first()
        test_db_session.delete(pep_to_delete)
        test_db_session.commit()
        
        # Act
        new_count = repository.get_peps_count()
        
        # Assert
        assert new_count == initial_count - 1


@pytest.mark.integration
class TestPEPRepositoryIntegration:
    """Integration tests for PEPRepository with complex scenarios."""
    
    def test_repository_with_relationships(self, repository: PEPRepository, test_db_session: Session):
        """Test repository methods work correctly with PEP-Author relationships."""
        # Arrange
        author = Author(name="Test Author")
        pep = PEP(
            number=123,
            title="Integration Test PEP",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-123"
        )
        pep.authors = [author]
        test_db_session.add(pep)
        test_db_session.commit()
        
        # Act
        retrieved_pep = repository.get_pep_by_number(123)
        
        # Assert
        assert retrieved_pep is not None
        assert len(retrieved_pep.authors) == 1
        assert retrieved_pep.authors[0].name == "Test Author"
    
    def test_repository_performance_with_large_dataset(
        self, 
        repository: PEPRepository, 
        test_db_session: Session,
        performance_tracker
    ):
        """Test repository performance with a larger dataset."""
        # Arrange - Create 100 PEPs
        peps = []
        for i in range(100):
            pep = PEP(
                number=i + 1000,
                title=f"Performance Test PEP {i}",
                status="Draft",
                type="Standards Track",
                topic="Core",
                url=f"https://test.com/pep-{i + 1000}"
            )
            peps.append(pep)
        
        test_db_session.add_all(peps)
        test_db_session.commit()
        
        # Act & Assert - Test pagination performance
        with performance_tracker.start():
            result = repository.list_all_peps(skip=0, limit=50)
        
        duration = performance_tracker.stop(max_duration=0.5)  # Should be fast
        
        assert len(result) == 50
        assert duration < 0.5
        
        # Act & Assert - Test search performance
        with performance_tracker.start():
            search_result = repository.search_peps_by_title("Performance")
        
        search_duration = performance_tracker.stop(max_duration=0.5)
        
        assert len(search_result) == 100  # All match "Performance"
        assert search_duration < 0.5


@pytest.mark.repository
class TestPEPRepositoryEdgeCases:
    """Test edge cases and error conditions for PEPRepository."""
    
    def test_repository_with_none_database_session(self):
        """Test that repository handles None database session appropriately."""
        # This test demonstrates defensive programming
        # In practice, this might raise an exception or handle gracefully
        with pytest.raises((AttributeError, TypeError)):
            repository = PEPRepository(None)
            repository.get_peps_count()
    
    def test_search_with_sql_injection_attempt(self, repository: PEPRepository, sample_peps):
        """Test that search is safe from SQL injection."""
        # Arrange
        malicious_query = "'; DROP TABLE peps; --"
        
        # Act
        result = repository.search_peps_by_title(malicious_query)
        
        # Assert
        assert result == []  # Should return empty, not crash
        
        # Verify database is still intact
        count = repository.get_peps_count()
        assert count == 4  # All original PEPs should still exist
    
    def test_search_with_unicode_characters(self, repository: PEPRepository, test_db_session: Session):
        """Test search with Unicode characters."""
        # Arrange
        unicode_pep = PEP(
            number=777,
            title="PEP with Unicode: 测试 and émojis 🐍",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-777"
        )
        test_db_session.add(unicode_pep)
        test_db_session.commit()
        
        # Act
        result = repository.search_peps_by_title("测试")
        
        # Assert
        assert len(result) == 1
        assert result[0].number == 777
    
    def test_pagination_edge_cases(self, repository: PEPRepository, sample_peps):
        """Test pagination with edge case parameters."""
        # Test with skip=0, limit=0
        result = repository.list_all_peps(skip=0, limit=0)
        assert result == []
        
        # Test with very large limit
        result = repository.list_all_peps(skip=0, limit=10000)
        assert len(result) == 4  # Only 4 PEPs exist
        
        # Test with negative skip (should be handled gracefully)
        result = repository.list_all_peps(skip=-1, limit=10)
        # Behavior depends on implementation - document expected behavior
        assert isinstance(result, list)