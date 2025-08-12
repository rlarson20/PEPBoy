"""
Factory Boy factories for generating test data.

This module provides factory classes for creating model instances
with realistic test data using Factory Boy and Faker.
"""

import datetime
from typing import Any

import factory
from factory import fuzzy
from faker import Faker

from src.models.orm_models import Author, PEP

fake = Faker()


class AuthorFactory(factory.Factory):
    """Factory for creating Author instances."""
    
    class Meta:
        model = Author
    
    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda obj: fake.name())
    
    @classmethod
    def create_batch_with_unique_names(cls, size: int, **kwargs) -> list[Author]:
        """Create a batch of authors with guaranteed unique names."""
        names = set()
        authors = []
        
        for _ in range(size):
            while True:
                name = fake.name()
                if name not in names:
                    names.add(name)
                    break
            
            author = cls.build(name=name, **kwargs)
            authors.append(author)
        
        return authors


class PEPFactory(factory.Factory):
    """Factory for creating PEP instances."""
    
    class Meta:
        model = PEP
    
    number = factory.Sequence(lambda n: n + 1)
    title = factory.LazyAttribute(
        lambda obj: fake.sentence(nb_words=6).replace(".", "")
    )
    discussions_to = factory.LazyAttribute(lambda obj: fake.email())
    status = fuzzy.FuzzyChoice([
        "Draft", "Final", "Accepted", "Rejected", "Withdrawn", 
        "Deferred", "Superseded", "Active"
    ])
    type = fuzzy.FuzzyChoice([
        "Standards Track", "Informational", "Process"
    ])
    topic = fuzzy.FuzzyChoice([
        "Core", "Library", "Typing", "Packaging", "Interoperability"
    ])
    created = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date="-10y", end_date="today")
    )
    python_version = fuzzy.FuzzyChoice([
        "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", None
    ])
    post_history = factory.LazyAttribute(
        lambda obj: fake.text(max_nb_chars=200) if fake.boolean() else None
    )
    resolution = factory.LazyAttribute(
        lambda obj: fake.url() if fake.boolean(chance_of_getting_true=30) else None
    )
    requires = factory.LazyAttribute(
        lambda obj: str(fake.random_int(min=1, max=500)) if fake.boolean(chance_of_getting_true=20) else None
    )
    replaces = factory.LazyAttribute(
        lambda obj: str(fake.random_int(min=1, max=500)) if fake.boolean(chance_of_getting_true=15) else None
    )
    superseded_by = factory.LazyAttribute(
        lambda obj: str(fake.random_int(min=1, max=500)) if fake.boolean(chance_of_getting_true=10) else None
    )
    url = factory.LazyAttribute(lambda obj: f"https://peps.python.org/pep-{obj.number:04d}/")


class PEPWithAuthorsFactory(PEPFactory):
    """Factory for creating PEP instances with associated authors."""
    
    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        """Add authors to the PEP after creation."""
        if not create:
            # Build mode, just return
            return
        
        if extracted:
            # If specific authors were provided, use them
            for author in extracted:
                self.authors.append(author)
        else:
            # Create random number of authors (1-3)
            num_authors = fake.random_int(min=1, max=3)
            authors = AuthorFactory.create_batch_with_unique_names(num_authors)
            for author in authors:
                self.authors.append(author)


# =============================================================================
# Specialized Factories
# =============================================================================

class DraftPEPFactory(PEPFactory):
    """Factory for creating PEP instances with Draft status."""
    
    status = "Draft"
    resolution = None
    superseded_by = None


class FinalPEPFactory(PEPFactory):
    """Factory for creating PEP instances with Final status."""
    
    status = "Final"
    resolution = factory.LazyAttribute(lambda obj: fake.url())


class AcceptedPEPFactory(PEPFactory):
    """Factory for creating PEP instances with Accepted status."""
    
    status = "Accepted"
    resolution = factory.LazyAttribute(lambda obj: fake.url())


class RejectedPEPFactory(PEPFactory):
    """Factory for creating PEP instances with Rejected status."""
    
    status = "Rejected"
    resolution = factory.LazyAttribute(lambda obj: fake.url())


class StandardsTrackPEPFactory(PEPFactory):
    """Factory for creating Standards Track PEP instances."""
    
    type = "Standards Track"
    topic = "Core"
    python_version = fuzzy.FuzzyChoice(["3.9", "3.10", "3.11", "3.12", "3.13"])


class InformationalPEPFactory(PEPFactory):
    """Factory for creating Informational PEP instances."""
    
    type = "Informational"
    python_version = None


class ProcessPEPFactory(PEPFactory):
    """Factory for creating Process PEP instances."""
    
    type = "Process"
    python_version = None
    topic = "Core"


# =============================================================================
# Batch Creation Utilities
# =============================================================================

class BatchFactory:
    """Utility class for creating batches of related test data."""
    
    @staticmethod
    def create_pep_collection(
        size: int = 10,
        with_authors: bool = True,
        status_distribution: dict[str, float] | None = None,
    ) -> list[PEP]:
        """
        Create a collection of PEPs with varied characteristics.
        
        Args:
            size: Number of PEPs to create
            with_authors: Whether to create authors for the PEPs
            status_distribution: Dictionary mapping status to probability
        
        Returns:
            List of PEP instances
        """
        if status_distribution is None:
            status_distribution = {
                "Draft": 0.3,
                "Final": 0.25,
                "Accepted": 0.2,
                "Rejected": 0.15,
                "Withdrawn": 0.1,
            }
        
        peps = []
        factory_map = {
            "Draft": DraftPEPFactory,
            "Final": FinalPEPFactory,
            "Accepted": AcceptedPEPFactory,
            "Rejected": RejectedPEPFactory,
        }
        
        for i in range(size):
            # Determine status based on distribution
            status = fake.random_element(elements=list(status_distribution.keys()))
            factory_class = factory_map.get(status, PEPFactory)
            
            if with_authors:
                pep = PEPWithAuthorsFactory.build(
                    number=i + 1,
                    status=status
                )
            else:
                pep = factory_class.build(number=i + 1)
            
            peps.append(pep)
        
        return peps
    
    @staticmethod
    def create_author_collection(size: int = 5) -> list[Author]:
        """Create a collection of unique authors."""
        return AuthorFactory.create_batch_with_unique_names(size)


# =============================================================================
# API Response Factories
# =============================================================================

class PEPAPIResponseFactory:
    """Factory for creating API response data structures."""
    
    @staticmethod
    def create_peps_json_response(pep_count: int = 5) -> dict[str, dict[str, Any]]:
        """
        Create a JSON response similar to what the PEP API returns.
        
        Args:
            pep_count: Number of PEPs to include in the response
        
        Returns:
            Dictionary representing the API response
        """
        peps = BatchFactory.create_pep_collection(size=pep_count, with_authors=True)
        response = {}
        
        for pep in peps:
            response[str(pep.number)] = {
                "number": pep.number,
                "title": pep.title,
                "authors": [author.name for author in pep.authors] if pep.authors else [],
                "discussions_to": pep.discussions_to,
                "status": pep.status,
                "type": pep.type,
                "topic": pep.topic,
                "created": pep.created.isoformat() if pep.created else None,
                "python_version": pep.python_version,
                "post_history": pep.post_history,
                "resolution": pep.resolution,
                "requires": pep.requires,
                "replaces": pep.replaces,
                "superseded_by": pep.superseded_by,
                "url": pep.url,
            }
        
        return response


# =============================================================================
# Test Scenario Factories
# =============================================================================

class TestScenarioFactory:
    """Factory for creating specific test scenarios."""
    
    @staticmethod
    def create_pep_with_dependencies() -> tuple[PEP, PEP, PEP]:
        """
        Create a set of PEPs with dependency relationships.
        
        Returns:
            Tuple of (original_pep, replacing_pep, superseding_pep)
        """
        original_pep = PEPFactory.build(
            number=100,
            status="Superseded",
            superseded_by="101"
        )
        
        replacing_pep = PEPFactory.build(
            number=101,
            status="Final",
            replaces="100",
            requires="102"
        )
        
        required_pep = PEPFactory.build(
            number=102,
            status="Final"
        )
        
        return original_pep, replacing_pep, required_pep
    
    @staticmethod
    def create_author_with_multiple_peps() -> tuple[Author, list[PEP]]:
        """
        Create an author with multiple PEPs.
        
        Returns:
            Tuple of (author, list_of_peps)
        """
        author = AuthorFactory.build()
        peps = []
        
        for i in range(3):
            pep = PEPFactory.build(number=i + 1)
            pep.authors = [author]
            peps.append(pep)
        
        return author, peps