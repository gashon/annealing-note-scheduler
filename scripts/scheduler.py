"""
This script is responsible for scheduling notes to be reviewed in the future
The script will scan the vaults directory for all markdown files and add them to the database.json file. If a note is already in the database, it will be skipped.
The script will schedule the following review dates: 1 day, 3 days, 7 days.
"""

import datetime
import json
import os
from enum import StrEnum
from typing import TypedDict

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
VAULTS_PATH = os.path.join(PARENT_DIR, 'vaults')
DATABASE_PATH = os.path.join(PARENT_DIR, 'database.json')

class Status(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Row(TypedDict):
    note_id: str
    absolute_path: str
    parent_dirs: list[str]
    jobs: list[dict]

type DB = list[Row]

def note_is_scheduled(note_path: str, db_ro: DB) -> bool:
    if db_ro:
        paths = [row['absolute_path'] for row in db_ro]
        return note_path in paths

    return False

def schedule_jobs(note_path: dict[str], db_rw: DB) -> DB:
    note_id = note_path["absolute_path"].split('/')[-1].split('.')[0]

    if note_is_scheduled(note_path["absolute_path"], db_rw):
        return db_rw

    today = datetime.date.today()
    jobs = [datetime.timedelta(days=1), datetime.timedelta(days=3), datetime.timedelta(days=7)]

    row: Row = {
        "note_id": note_id,
        "absolute_path": note_path["absolute_path"],
        "parent_dirs": note_path["parent_dirs"],
        "jobs": [{"status": Status.PENDING, "date": str(today + job)} for job in jobs]
    }

    db_rw.append(row)
    return db_rw


def get_note_filepaths() -> list[dict]:
    note_filepaths = []

    def recurse_directory(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    absolute_path = os.path.join(root, file)
                    relative_path = os.path.relpath(absolute_path, VAULTS_PATH)
                    parent_dirs = os.path.dirname(relative_path).split(os.sep)
                    
                    parent_dirs = [d for d in parent_dirs if d]

                    note_filepaths.append({"absolute_path": absolute_path, "parent_dirs": parent_dirs})
    
    recurse_directory(VAULTS_PATH)
    return note_filepaths


def main():
    note_filepaths = get_note_filepaths()

    with open(DATABASE_PATH, 'r') as f:
        db_rw: DB = json.load(f)

    for note_path in note_filepaths:
        db_rw = schedule_jobs(note_path, db_rw)

    with open(DATABASE_PATH, 'w') as f:
        json.dump(db_rw, f, indent=4)


if __name__ == '__main__':
    main()

