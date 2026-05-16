import unittest

import app.entities  # noqa: F401 — load entity modules for mapper registration
from app.db.orm import Base, engine
from app.entities import TABLE_NAMES
from sqlalchemy import text
from sqlalchemy.orm import configure_mappers


class TestORMMetadata(unittest.TestCase):
    def test_expected_tables_registered(self) -> None:
        names = set(Base.metadata.tables.keys())
        self.assertEqual(names, TABLE_NAMES)

    def test_configure_mappers_idempotent(self) -> None:
        configure_mappers()
        configure_mappers()

    def test_sqlite_foreign_keys_enabled_on_orm_connections(self) -> None:
        with engine.connect() as conn:
            enabled = conn.execute(text("PRAGMA foreign_keys")).scalar_one()
        self.assertEqual(enabled, 1)


if __name__ == "__main__":
    unittest.main()
