"""
Unit tests for ORM models.

This module demonstrates TDD red-green-refactor methodology
by testing model validation, relationships, and business logic.
"""

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.orm_models import Author, PEP, pep_author_association
from tests.fixtures.factories import (
    AuthorFactory, 
    PEPFactory, 
    TestScenarioFactory,
    BatchFactory
)


class TestAuthorModel:
    """Test cases for the Author model."""
    
    def test_author_creation_success(self, test_db_session: Session):
        """Test successful creation of an Author instance.
        
        TDD Red: Write test expecting author creation to work
        TDD Green: Implement minimal Author model
        TDD Refactor: Add validation and constraints
        """
        # Arrange
        author_data = {
            "name": "Guido van Rossum"
        }
        
        # Act
        author = Author(**author_data)
        test_db_session.add(author)
        test_db_session.commit()
        
        # Assert
        assert author.id is not None
        assert author.name == "Guido van Rossum"
        assert str(author) == f"<Author(id={author.id}, name='Guido van Rossum')>"
    
    def test_author_unique_name_constraint(self, test_db_session: Session):
        """Test that author names must be unique."""
        # Arrange
        name = "Guido van Rossum"
        
        # Act & Assert
        author1 = Author(name=name)
        test_db_session.add(author1)
        test_db_session.commit()
        
        # Try to create another author with the same name
        author2 = Author(name=name)
        test_db_session.add(author2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_author_name_required(self, test_db_session: Session):
        """Test that author name is required."""
        # Arrange & Act & Assert
        author = Author()
        test_db_session.add(author)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_author_peps_relationship(self, test_db_session: Session):
        """Test the many-to-many relationship between authors and PEPs."""
        # Arrange
        author = Author(name="Test Author")
        pep1 = PEP(
            number=1,
            title="Test PEP 1",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-1"
        )
        pep2 = PEP(
            number=2,
            title="Test PEP 2", 
            status="Final",
            type="Informational",
            topic="Library",
            url="https://test.com/pep-2"
        )
        
        # Act
        author.peps = [pep1, pep2]
        test_db_session.add(author)
        test_db_session.commit()
        
        # Assert
        retrieved_author = test_db_session.query(Author).filter_by(name="Test Author").first()
        assert len(retrieved_author.peps) == 2
        assert pep1 in retrieved_author.peps
        assert pep2 in retrieved_author.peps


class TestPEPModel:
    """Test cases for the PEP model."""
    
    def test_pep_creation_success(self, test_db_session: Session):
        """Test successful creation of a PEP instance."""
        # Arrange
        pep_data = {
            "number": 1,
            "title": "PEP Purpose and Guidelines",
            "status": "Active",
            "type": "Process", 
            "topic": "Core",
            "created": date(2000, 6, 13),
            "url": "https://peps.python.org/pep-0001/"
        }
        
        # Act
        pep = PEP(**pep_data)
        test_db_session.add(pep)
        test_db_session.commit()
        
        # Assert
        assert pep.number == 1
        assert pep.title == "PEP Purpose and Guidelines"
        assert pep.status == "Active"
        assert pep.type == "Process"
        assert pep.topic == "Core"
        assert pep.created == date(2000, 6, 13)
        assert pep.url == "https://peps.python.org/pep-0001/"
        assert "PEP(number=1" in str(pep)
    
    def test_pep_number_as_primary_key(self, test_db_session: Session):
        """Test that PEP number serves as the primary key."""
        # Arrange & Act
        pep1 = PEP(
            number=100,
            title="Test PEP",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-100"
        )
        test_db_session.add(pep1)
        test_db_session.commit()
        
        # Try to create another PEP with the same number
        pep2 = PEP(
            number=100,
            title="Another Test PEP", 
            status="Final",
            type="Informational",
            topic="Library",
            url="https://test.com/pep-100-alt"
        )
        test_db_session.add(pep2)
        
        # Assert
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_pep_required_fields(self, test_db_session: Session):
        """Test that required fields are enforced."""
        # Test missing number
        with pytest.raises(TypeError):
            PEP(title="Test", status="Draft", type="Standards Track", topic="Core", url="test.com")
        
        # Test missing title
        with pytest.raises(TypeError):
            PEP(number=1, status="Draft", type="Standards Track", topic="Core", url="test.com")
    
    def test_pep_optional_fields(self, test_db_session: Session):
        """Test that optional fields can be None."""
        # Arrange & Act
        pep = PEP(
            number=200,
            title="Test PEP with Nulls",
            status="Draft",
            type="Standards Track", 
            topic="Core",
            url="https://test.com/pep-200",
            discussions_to=None,
            created=None,
            python_version=None,
            post_history=None,
            resolution=None,
            requires=None,
            replaces=None,
            superseded_by=None
        )
        test_db_session.add(pep)
        test_db_session.commit()
        
        # Assert
        assert pep.discussions_to is None
        assert pep.created is None
        assert pep.python_version is None
        assert pep.post_history is None
        assert pep.resolution is None
        assert pep.requires is None
        assert pep.replaces is None
        assert pep.superseded_by is None
    
    def test_pep_authors_relationship(self, test_db_session: Session):
        """Test the many-to-many relationship between PEPs and authors."""
        # Arrange
        author1 = Author(name="Author One")
        author2 = Author(name="Author Two")
        pep = PEP(
            number=300,
            title="Multi-Author PEP",
            status="Draft",
            type="Standards Track",
            topic="Core", 
            url="https://test.com/pep-300"
        )
        
        # Act
        pep.authors = [author1, author2]
        test_db_session.add(pep)
        test_db_session.commit()
        
        # Assert
        retrieved_pep = test_db_session.query(PEP).filter_by(number=300).first()
        assert len(retrieved_pep.authors) == 2
        assert author1 in retrieved_pep.authors
        assert author2 in retrieved_pep.authors


class TestPEPAuthorAssociation:
    """Test cases for the PEP-Author association table."""
    
    def test_association_table_creation(self, test_db_session: Session):
        """Test that the association table works correctly."""
        # Arrange
        author = Author(name="Association Test Author")
        pep = PEP(
            number=400,
            title="Association Test PEP",
            status="Draft",
            type="Standards Track", 
            topic="Core",
            url="https://test.com/pep-400"
        )
        
        # Act
        # Create association through the relationship
        author.peps.append(pep)
        test_db_session.add(author)
        test_db_session.commit()
        
        # Assert
        # Check that the association exists
        result = test_db_session.execute(
            pep_author_association.select().where(
                pep_author_association.c.pep_number == 400
            )
        ).fetchone()
        
        assert result is not None
        assert result.pep_number == 400
        assert result.author_id == author.id
    
    def test_cascade_deletion_behavior(self, test_db_session: Session):
        """Test behavior when deleting authors or PEPs with associations."""
        # Arrange
        author = Author(name="Delete Test Author")
        pep = PEP(
            number=500,
            title="Delete Test PEP",
            status="Draft",
            type="Standards Track",
            topic="Core",
            url="https://test.com/pep-500"
        )
        author.peps.append(pep)
        test_db_session.add(author)
        test_db_session.commit()
        
        # Act - Delete the author
        test_db_session.delete(author)
        test_db_session.commit()
        
        # Assert - PEP should still exist, but association should be gone
        remaining_pep = test_db_session.query(PEP).filter_by(number=500).first()
        assert remaining_pep is not None
        assert len(remaining_pep.authors) == 0


class TestModelFactories:
    """Test cases for model factories to ensure they work correctly."""
    
    def test_author_factory(self):
        """Test that AuthorFactory creates valid instances."""
        # Act
        author = AuthorFactory.build()
        
        # Assert
        assert isinstance(author, Author)
        assert author.name is not None
        assert len(author.name) > 0
    
    def test_pep_factory(self):
        """Test that PEPFactory creates valid instances."""
        # Act
        pep = PEPFactory.build()
        
        # Assert
        assert isinstance(pep, PEP)
        assert pep.number is not None
        assert pep.title is not None
        assert pep.status in ["Draft", "Final", "Accepted", "Rejected", "Withdrawn", "Deferred", "Superseded", "Active"]
        assert pep.type in ["Standards Track", "Informational", "Process"]
        assert pep.url is not None
    
    def test_batch_factory_pep_collection(self):
        """Test BatchFactory creates consistent collections."""
        # Act
        peps = BatchFactory.create_pep_collection(size=5, with_authors=True)
        
        # Assert
        assert len(peps) == 5
        assert all(isinstance(pep, PEP) for pep in peps)
        assert all(len(pep.authors) > 0 for pep in peps)
        
        # Check that numbers are sequential
        numbers = [pep.number for pep in peps]
        assert numbers == [1, 2, 3, 4, 5]
    
    def test_test_scenario_factory(self):
        """Test that TestScenarioFactory creates related PEPs correctly."""
        # Act
        original, replacing, required = TestScenarioFactory.create_pep_with_dependencies()
        
        # Assert
        assert original.superseded_by == "101"
        assert replacing.replaces == "100"
        assert replacing.requires == "102"
        assert original.number == 100
        assert replacing.number == 101
        assert required.number == 102


@pytest.mark.slow
class TestModelPerformance:
    """Performance tests for model operations."""
    
    def test_bulk_author_creation_performance(self, test_db_session: Session, performance_tracker):
        """Test performance of creating many authors."""
        # Arrange
        num_authors = 1000
        
        # Act
        with performance_tracker.start():
            authors = []
            for i in range(num_authors):
                author = Author(name=f"Author {i}")
                authors.append(author)
            
            test_db_session.add_all(authors)
            test_db_session.commit()
        
        duration = performance_tracker.stop(max_duration=2.0)  # Should complete within 2 seconds
        
        # Assert
        count = test_db_session.query(Author).count()
        assert count == num_authors
        assert duration < 2.0
    
    def test_relationship_query_performance(self, test_db_session: Session, performance_tracker):
        """Test performance of querying relationships."""
        # Arrange - Create test data
        authors = [Author(name=f"Perf Author {i}") for i in range(10)]
        peps = []
        
        for i in range(50):
            pep = PEP(
                number=i + 1000,
                title=f"Performance Test PEP {i}",
                status="Draft",
                type="Standards Track",
                topic="Core",
                url=f"https://test.com/pep-{i + 1000}"
            )
            # Assign 1-3 random authors to each PEP
            import random
            pep.authors = random.sample(authors, k=random.randint(1, 3))
            peps.append(pep)
        
        test_db_session.add_all(authors + peps)
        test_db_session.commit()
        
        # Act - Query with relationships
        with performance_tracker.start():
            results = test_db_session.query(PEP).filter(
                PEP.number >= 1000
            ).all()
            
            # Access the relationships to trigger loading
            for pep in results:
                _ = len(pep.authors)
        
        duration = performance_tracker.stop(max_duration=1.0)
        
        # Assert
        assert len(results) == 50
        assert duration < 1.0