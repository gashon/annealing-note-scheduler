# Annealing Note Scheduler

System to email a copy of markdown notes on an annealing schedule to combat the [forgetting curve](https://en.wikipedia.org/wiki/Forgetting_curve).

Use a cronjob to frequently "schedule" jobs, adding them to the db if not already present for scheduling.

Create another cronjob that runs daily to "execute" the jobs, sending all of the notes that are scheduled to be sent on that day.

Periodically `rsync` local obsidian vault to the worker w/ an async cron service.


### Commands 

```python
PYTHONPATH=./ python3 scripts/execute_jobs.py
```

```python
PYTHONPATH=./ python3 scripts/schedule.py
```

