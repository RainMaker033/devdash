# DevDash Testing Guide

Follow these steps to test DevDash!

## Before You Start

Open TWO terminal windows:
- **Terminal 1**: Run DevDash (the dashboard)
- **Terminal 2**: Keep this guide open or make changes to test Git panel

---

## Terminal 1: Start DevDash

```bash
cd ~/Downloads/devdash
source venv/bin/activate
devdash
```

When DevDash starts, you'll see 4 panels. Let's test each one!

---

## Test 1: Help Modal ⭐

**Press:** `?`

**Expected:**
- A help popup appears showing all keyboard shortcuts
- Press `ESC` or `q` to close it

**Status:** ⬜ Tested

---

## Test 2: Git Panel (Top Left) ⭐

**What you should see:**
- Branch: main
- Status: Clean (or Modified)
- Last 3 commits

**To test changes:**
1. Keep DevDash running in Terminal 1
2. In Terminal 2, run:
   ```bash
   cd ~/Downloads/devdash
   echo "test" >> test.txt
   ```
3. Wait 5 seconds
4. Watch Git panel update to show "Modified"

**Status:** ⬜ Tested

---

## Test 3: System Panel (Top Right) ⭐

**What you should see:**
- CPU usage with colored bar (green/yellow/red)
- RAM usage with progress bar
- Disk usage
- Session uptime

**To test:**
- Watch CPU percentage change in real-time
- Open another app to see CPU/RAM spike

**Status:** ⬜ Tested

---

## Test 4: Tasks Panel (Bottom Left) ⭐⭐⭐

### Add your first task:
1. Press `a`
2. Type: `Test the Pomodoro timer`
3. Press Enter

### Add more tasks:
1. Press `a`
2. Type: `Review the code`
3. Press Enter
4. Press `a`
5. Type: `Write documentation`
6. Press Enter

### Navigate tasks:
- Press `↓` (down arrow) - moves to next task
- Press `↑` (up arrow) - moves to previous task

### Toggle completion:
- Press `space` - marks task as done [✓]
- Press `space` again - marks as undone [ ]

### Delete a task:
- Use arrows to select a task
- Press `d` - task is deleted

**Status:** ⬜ Tested

---

## Test 5: Timer Panel (Bottom Right) ⭐⭐

### Start Focus Session:
1. Press `f`
2. Watch countdown: 25:00 → 24:59 → 24:58...
3. See progress bar decrease
4. Wait a few seconds

### Stop Timer:
1. Press `s`
2. Timer returns to IDLE state

### Start Break:
1. Press `b`
2. Watch countdown: 05:00 → 04:59...
3. Press `s` to stop

**Status:** ⬜ Tested

---

## Test 6: Refresh ⭐

**Press:** `r`

**Expected:**
- All panels refresh their data
- Git panel re-checks repository
- System metrics update

**Status:** ⬜ Tested

---

## Test 7: Quit ⭐

**Press:** `q` (or `Ctrl+C`)

**Expected:**
- DevDash exits cleanly
- Returns to terminal prompt

**Status:** ⬜ Tested

---

## Test 8: Verify Tasks Were Saved

After quitting DevDash, check the tasks file:

```bash
cd ~/Downloads/devdash
cat .devdash_tasks.json
```

You should see your tasks in JSON format!

**Status:** ⬜ Tested

---

## Test 9: Run Automated Tests

```bash
cd ~/Downloads/devdash
source venv/bin/activate
pytest -v
```

**Expected:** All 8 tests pass ✅

**Status:** ⬜ Tested

---

## Quick Reference Card

While DevDash is running:

| Key | Action |
|-----|--------|
| `?` | Show help |
| `q` | Quit |
| `r` | Refresh all |
| **Tasks** | |
| `a` | Add task |
| `space` | Toggle done |
| `d` | Delete task |
| `↑` `↓` | Navigate |
| **Timer** | |
| `f` | Start focus (25min) |
| `b` | Start break (5min) |
| `s` | Stop timer |

---

## Checklist Summary

- [ ] Help modal works
- [ ] Git panel shows repository info
- [ ] Git panel updates when files change
- [ ] System panel shows CPU/RAM/Disk
- [ ] Can add tasks
- [ ] Can navigate tasks with arrows
- [ ] Can toggle tasks done/undone
- [ ] Can delete tasks
- [ ] Timer starts and counts down
- [ ] Timer can be stopped
- [ ] Break timer works
- [ ] Refresh works
- [ ] Quit works
- [ ] Tasks persist to .devdash_tasks.json
- [ ] All pytest tests pass

---

**Ready? Let's start!** Open Terminal 1 and run DevDash!
