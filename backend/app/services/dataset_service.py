"""
Dataset service layer.

Handles dataset CRUD operations and file management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetUpdate


class DatasetService:
    """Service for dataset operations."""

    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
        """Get dataset by ID."""
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def get_datasets(
        db: Session,
        project_id: Optional[int] = None,
        dataset_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dataset]:
        """Get all datasets with optional filtering."""
        query = db.query(Dataset)

        if project_id is not None:
            query = query.filter(Dataset.project_id == project_id)

        if dataset_type is not None:
            query = query.filter(Dataset.dataset_type == dataset_type)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_dataset(db: Session, dataset: DatasetCreate) -> Dataset:
        """Create a new dataset."""
        db_dataset = Dataset(
            name=dataset.name,
            description=dataset.description,
            dataset_type=dataset.dataset_type,
            file_path=dataset.file_path,
            file_format=dataset.file_format,
            file_size_bytes=dataset.file_size_bytes,
            num_rows=dataset.num_rows,
            num_columns=dataset.num_columns,
            schema_info=dataset.schema_info,
            metadata=dataset.metadata,
            project_id=dataset.project_id,
        )
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        return db_dataset

    @staticmethod
    def update_dataset(
        db: Session,
        dataset_id: int,
        dataset_update: DatasetUpdate
    ) -> Optional[Dataset]:
        """Update an existing dataset."""
        db_dataset = DatasetService.get_dataset(db, dataset_id)
        if not db_dataset:
            return None

        update_data = dataset_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dataset, field, value)

        db.commit()
        db.refresh(db_dataset)
        return db_dataset

    @staticmethod
    def delete_dataset(db: Session, dataset_id: int) -> bool:
        """Delete a dataset."""
        db_dataset = DatasetService.get_dataset(db, dataset_id)
        if not db_dataset:
            return False

        db.delete(db_dataset)
        db.commit()
        return True

    @staticmethod
    def get_dataset_with_stats(db: Session, dataset_id: int) -> Optional[dict]:
        """Get dataset with usage statistics."""
        db_dataset = DatasetService.get_dataset(db, dataset_id)
        if not db_dataset:
            return None

        # Count how many experiments use this dataset
        from app.models.experiment import Experiment
        experiments_count = db.query(func.count(Experiment.id)).filter(
            Experiment.dataset_id == dataset_id
        ).scalar()

        dataset_dict = {
            "id": db_dataset.id,
            "name": db_dataset.name,
            "description": db_dataset.description,
            "dataset_type": db_dataset.dataset_type,
            "file_path": db_dataset.file_path,
            "file_format": db_dataset.file_format,
            "file_size_bytes": db_dataset.file_size_bytes,
            "num_rows": db_dataset.num_rows,
            "num_columns": db_dataset.num_columns,
            "schema_info": db_dataset.schema_info,
            "metadata": db_dataset.metadata,
            "project_id": db_dataset.project_id,
            "created_at": db_dataset.created_at,
            "updated_at": db_dataset.updated_at,
            "experiments_count": experiments_count,
        }

        return dataset_dict

    @staticmethod
    def get_datasets_summary(
        db: Session,
        project_id: Optional[int] = None
    ) -> List[dict]:
        """Get summary of all datasets."""
        query = db.query(Dataset)

        if project_id is not None:
            query = query.filter(Dataset.project_id == project_id)

        datasets = query.all()
        summaries = []

        for dataset in datasets:
            summaries.append({
                "id": dataset.id,
                "name": dataset.name,
                "dataset_type": dataset.dataset_type,
                "num_rows": dataset.num_rows,
                "file_size_bytes": dataset.file_size_bytes,
                "project_id": dataset.project_id,
                "created_at": dataset.created_at,
            })

        return summaries
