import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import health
from app.services.crud import clinical_repository


class TestDatabaseAvailability(unittest.TestCase):
    def test_health_reports_missing_file_without_connecting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing.db"
            mocked_engine = Mock()
            with (
                patch.object(health, "resolve_sqlite_path", return_value=missing_path),
                patch.object(health, "engine", mocked_engine),
            ):
                result = health.check_database_via_orm()

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "database_file_missing")
        mocked_engine.connect.assert_not_called()

    def test_health_reports_missing_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "empty.db"
            db_path.touch()
            engine = create_engine(f"sqlite:///{db_path.as_posix()}")
            with (
                patch.object(health, "resolve_sqlite_path", return_value=db_path),
                patch.object(health, "engine", engine),
            ):
                result = health.check_database_via_orm()
            engine.dispose()

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "database_schema_missing")
        self.assertIn("departments", result["missing_tables"])

    def test_clinical_repository_raises_domain_error_when_schema_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "empty.db"
            engine = create_engine(f"sqlite:///{db_path.as_posix()}")
            SessionLocal = sessionmaker(bind=engine)
            with SessionLocal() as db:
                with self.assertRaises(clinical_repository.DatabaseUnavailableError):
                    clinical_repository.list_departments(db)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
