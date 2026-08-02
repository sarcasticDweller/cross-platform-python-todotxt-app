# A Cross Platform Todo.txt app, written in Python

Codename Lalonde.

---

This is a student project to scratch an itch for a maintained FLOSS todo list app that works on desktop and mobile and handles its own alarms on Android.

The idea is that the app sits on top of a [todo.txt](http://todotxt.org/) file and serves its content. Because all of its data lives in a plain text file, that file can be synced with whatever you want.

## Setup

As of 2026-08-01 the source code is tested working on Debian Trixie and macOS Tahoe. You can get the program running by running the following in your terminal:

```shell
chmod +x scripts/setup_dev_env.sh
sudo scripts/setup_dev_env.sh
source .venv/bin/activate
touch tmp_todo.txt # required for the time being
python3 src/lalonde/main.py
```

## Project Objectives

Create a pytodo project that:

- Has desktop and mobile release
- Supports alarms on Android
- Is as Google independent as possible
- Consistently handles todo.txt across all devices
- Watches the todo.txt file for remote changes (Syncthing, anyone?) and updates the GUI dynamically
    - This requires the file be in a "read" mode by default and limit the amount of editing happening at any given moment
- Is feature complete
    - Task name, description, tags, and datetime data
    - Recurring tasks
    - Rescheduling tasks
