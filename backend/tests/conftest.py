"""
Pytest configuration and fixtures for all tests.

Provides shared fixtures for database, authentication, and test data.
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus


# ============================================
# Database Fixtures
# ============================================

@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine using SQLite in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ============================================
# User Fixtures
# ============================================

@pytest.fixture
def test_password() -> str:
    """Standard test password."""
    return "TestPass123!"


@pytest.fixture
def test_user(db_session: Session, test_password: str) -> User:
    """Create a standard test user (researcher role)."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash(test_password),
        role=UserRole.RESEARCHER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session, test_password: str) -> User:
    """Create a test admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash(test_password),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_viewer(db_session: Session, test_password: str) -> User:
    """Create a test viewer user."""
    user = User(
        email="viewer@example.com",
        username="viewer",
        full_name="Viewer User",
        hashed_password=get_password_hash(test_password),
        role=UserRole.VIEWER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================
# Authentication Fixtures
# ============================================

@pytest.fixture
def user_token(test_user: User) -> str:
    """Create JWT token for test user."""
    return create_access_token(
        subject=test_user.id,
        additional_claims={"role": test_user.role.value}
    )


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """Create JWT token for admin user."""
    return create_access_token(
        subject=test_admin.id,
        additional_claims={"role": test_admin.role.value}
    )


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Create authorization headers with user token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================
# Project Fixtures
# ============================================

@pytest.fixture
def test_project(db_session: Session, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="A test project for unit tests",
        status=ProjectStatus.ACTIVE,
        owner_id=test_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def multiple_projects(db_session: Session, test_user: User) -> list[Project]:
    """Create multiple test projects."""
    projects = [
        Project(
            name=f"Test Project {i}",
            description=f"Test project number {i}",
            status=ProjectStatus.ACTIVE if i % 2 == 0 else ProjectStatus.ARCHIVED,
            owner_id=test_user.id,
        )
        for i in range(1, 6)
    ]
    for project in projects:
        db_session.add(project)
    db_session.commit()
    for project in projects:
        db_session.refresh(project)
    return projects


# ============================================
# ML Test Data Fixtures
# ============================================

@pytest.fixture
def sample_smiles() -> list[str]:
    """Sample SMILES strings for molecule testing."""
    return [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "CC(C)NCC(COc1ccccc1)O",  # Propranolol
        "CN1C(=O)CN=C(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3",  # Diazepam
    ]


@pytest.fixture
def sample_molecular_properties() -> dict:
    """Sample molecular properties for testing."""
    return {
        "molecular_weight": 180.16,
        "logp": 1.19,
        "hbd": 1,
        "hba": 3,
        "tpsa": 63.6,
        "rotatable_bonds": 3,
        "aromatic_rings": 1,
    }


# ============================================
# Utility Fixtures
# ============================================

@pytest.fixture
def mock_celery_task(monkeypatch):
    """Mock Celery task execution."""
    def mock_apply_async(*args, **kwargs):
        class MockTask:
            def __init__(self):
                self.id = "mock-task-id-12345"
        return MockTask()

    return mock_apply_async
