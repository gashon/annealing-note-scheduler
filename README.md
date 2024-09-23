System to email a copy of markdown notes on an annealing schedule to combat forgetting curves.

Use a cronjob to frequently "schedule" jobs, adding them to the db if not already present for scheduling.

Create another cronjob that runs daily to "execute" the jobs, sending all of the notes that are scheduled to be sent on that day.

```python
PYTHONPATH=./ python3 scripts/execute_jobs.py
```

```python
PYTHONPATH=./ python3 scripts/schedule.py
```

