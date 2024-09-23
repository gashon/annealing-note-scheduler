import json
from datetime import datetime

import boto3

from scripts.scheduler import DATABASE_PATH, DB, Row, Status

SENDER_EMAIL = "gashon@ghussein.org"
RECIPIENT_EMAIL = "gashon96@gmail.com"

def is_scheduled_for_today(date_str: str) -> bool:
    return datetime.today().strftime('%Y-%m-%d') == date_str

def get_todays_jobs(db_rw: DB) -> list[tuple[int, int]]:
    db_idxs :list[tuple[int, int]] = []

    for db_idx, notes in enumerate(db_rw):
        for job_idx, job in enumerate(notes['jobs']):
            if is_scheduled_for_today(job['date']):
                if job["status"] != Status.COMPLETED:
                    db_idxs.append((db_idx, job_idx))
                    break

    return db_idxs

def send_email(ses_client: any, note_metadata: Row, note_content: str): 
    response = ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={
            'ToAddresses': [RECIPIENT_EMAIL]
        },
        Message={
            'Subject': {
                'Data': f'{"|".join(note_metadata["parent_dirs"])}: {note_metadata["note_id"]}'
            },
            'Body': {
                'Text': {
                    'Data': note_content
                }
            }
        }
    )

    print("RESPONSE", response)

def main():
    with open(DATABASE_PATH, 'r') as f:
        db_rw: DB = json.load(f)

    idxs = get_todays_jobs(db_rw)
    ses_client = boto3.client('ses', region_name='us-west-1')  

    for (db_idx, job_idx) in idxs:
        note_metadata = db_rw[db_idx]
        with open(note_metadata['absolute_path'], 'r') as f:
            note_content = f.read()

        #TODO(gashon): add error handling and logging/alerting
        try: 
            send_email(ses_client, note_metadata, note_content)
            db_rw[db_idx]['jobs'][job_idx]['status'] = Status.COMPLETED
        except Exception as e:
            print("Failed to send email", e)
            db_rw[db_idx]['jobs'][job_idx]['status'] = Status.FAILED

    with open(DATABASE_PATH, 'w') as f:
        json.dump(db_rw, f, indent=4)

if __name__ == '__main__':
    main()
