import os
from pathlib import Path
import tempfile

import pytest
from sqlalchemy.orm.exc import DetachedInstanceError

from src.core.db.game_worker import GameDBWorker
from src.core.db.models import (
    ClubDB,
    PersonDB,
    StaffDB,
    ContractDB,
)
from src.core.game_types import PersonalityType, StaffRole, ReputationLevel, ContractType
from src.core.db.utils import create_tables


def setup_basic_club(db_path: str) -> tuple[ClubDB, StaffDB]:
    """Create a simple club with one staff member and return both objects.

    A fresh database will be created at *db_path* (existing file removed).
    """
    create_tables(db_path, delete_existing=True)
    gw = GameDBWorker(db_path=db_path)
    worker = gw.worker
    session = worker.session

    # create objects and commit
    club = ClubDB(name="Test Club")
    person = PersonDB(
        first_name="John",
        last_name="Doe",
        age=30,
        personality=PersonalityType.Rash,
    )
    staff = StaffDB(
        role=StaffRole.Manager,
        reputation_type=ReputationLevel.Good,
        ability=5,
        person=person,
    )
    contract = ContractDB(
        person=person,
        club=club,
        expiry_date=2025,
        wage=100,
        contract_type=ContractType.Staff_Contract,
    )
    session.add_all([club, person, staff, contract])
    session.commit()
    return club, staff


def test_staff_members_lazy_loads_without_detaching(tmp_path):
    # prepare a temporary file path for the database
    db_file = str(tmp_path / "test.db")
    club, staff = setup_basic_club(db_file)

    gw = GameDBWorker(db_path=db_file)
    # retrieve club using the same worker instance several times and ensure
    # the returned object remains bound to the session while in use.
    club_obj = gw.worker.get_club(club.id)

    # attribute access that normally triggers a lazy load should not raise
    try:
        members = club_obj.staff_members()
    except DetachedInstanceError:
        pytest.fail("Club instance was detached from session during access")

    assert len(members) == 1
    # retrieved object may not be the same Python instance as the one we
    # originally added; compare by primary key instead.
    assert members[0].person_id == staff.person_id

    # manually close the session and verify the eager-loaded data still works
    gw.worker.close_session()
    # after closing the session, accessing the relationship again should not
    # raise because it was fetched eagerly in the original query
    members_again = club_obj.staff_members()
    assert len(members_again) == 1
    assert members_again[0].person_id == staff.person_id



def test_worker_caching(tmp_path):
    """Multiple accesses to the `worker` property should return the same object."""
    db_file = str(tmp_path / "test2.db")
    create_tables(db_file, delete_existing=True)
    gw = GameDBWorker(db_path=db_file)
    w1 = gw.worker
    w2 = gw.worker
    assert w1 is w2

    # closing should clear the cache and create a new one on next access
    gw.close()
    w3 = gw.worker
    assert w3 is not w1
