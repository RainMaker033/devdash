# Configuration Editor Guide

The DevDash configuration editor provides a visual TUI interface for modifying settings without manually editing TOML files.

## Opening the Editor

**From within DevDash:**
- Press `c` to open the configuration editor
- Or check the help menu with `?` and look under "General"

## Using the Editor

### Navigation

**Moving Between Fields:**
- **Tab** - Move to next field (forward)
- **Shift+Tab** - Move to previous field (backward)
- **Mouse Click** - Click directly on any input field

**Scrolling:**
- **Mouse Wheel** - Scroll up/down to see all settings
- **Page Up / Page Down** - Scroll by page
- **↑ / ↓** arrow keys - Scroll when not in an input field

**Editing:**
- **Click in a field** or **Tab to it** to start editing
- **Type** your new value
- **Tab** to move to next field (your changes are saved automatically)

### Editing Settings

The editor shows settings organized by panel:

1. **Git Panel**
   - Refresh Interval - How often to check git status (seconds)
   - Max Commits - Number of recent commits to display

2. **System Panel**
   - Refresh Interval - Update frequency (seconds)
   - CPU Warning % - Yellow threshold
   - CPU Critical % - Red threshold
   - Progress Bar Width - Size of progress bars

3. **Tasks Panel**
   - File Path - Location of tasks JSON file
   - Default Sort - Initial sort order (created/priority/due_date/text)
   - Max Visible Tasks - How many tasks to show

4. **Timer Panel**
   - Focus Duration - Pomodoro focus time (minutes)
   - Break Duration - Break time (minutes)
   - Progress Bar Width - Timer progress bar size

### Saving Changes

**Two ways to save:**
1. Press `Ctrl+S` (keyboard shortcut)
2. Click the "Save" button

If there are validation errors, you'll see a red error message. Fix the issues and try saving again.

**Success:** When saved successfully, you'll see a green message showing where the config was saved.

### Canceling

**Two ways to cancel:**
1. Press `Esc` (keyboard shortcut)
2. Click the "Cancel" button

No changes will be saved.

## Where Configs Are Saved

The editor saves to the first found config file, or creates one in:
1. `./.devdash.toml` (current directory) - if a config already exists here
2. `~/.config/devdash/config.toml` (user config) - if it exists there
3. `./.devdash.toml` (current directory) - default for new configs

**Note:** After saving, restart DevDash to see the changes take effect.

## Validation Rules

The editor validates your input:

- **Intervals** must be positive numbers
- **Thresholds** must be 0-100
- **Warning must be < Critical** for system thresholds
- **Sort options** must be valid: created, priority, due_date, or text
- **Durations** must be positive integers

Invalid values will show error messages and prevent saving.

## Tips

1. **Start simple** - Change one setting at a time
2. **Validate first** - The editor won't save invalid configs
3. **Test immediately** - Restart DevDash after saving to see changes
4. **Keep defaults** - Only change what you need

## Examples

### Longer Pomodoro Sessions
1. Press `c` to open editor
2. Scroll to Timer Panel
3. Change Focus Duration to `50`
4. Change Break Duration to `10`
5. Press `Ctrl+S` to save

### Less Frequent Git Updates
1. Press `c` to open editor
2. Find Git Panel
3. Change Refresh Interval to `10`
4. Press `Ctrl+S` to save

### Custom CPU Thresholds
1. Press `c` to open editor
2. Find System Panel
3. Change CPU Warning to `70.0`
4. Change CPU Critical to `90.0`
5. Press `Ctrl+S` to save

## Troubleshooting

**Editor won't open:**
- Make sure you're running the latest version
- Check that you pressed lowercase `c`

**Can't save:**
- Check the error message at the bottom
- Fix any validation errors shown in red
- Make sure values are numbers where expected

**Changes not showing:**
- Remember to restart DevDash after saving
- Check the config file was actually saved (use `--show-config`)

**Want to reset:**
- Delete your config file and restart DevDash
- Or manually edit the file to remove settings

## Advanced: CLI Alternative

You can also manage configs via CLI:

```bash
# View current config
devdash --show-config

# Validate config file
devdash --validate-config

# Generate example config
devdash --generate-config > my-config.toml

# Use specific config
devdash --config my-config.toml
```

---

**Note:** The config editor is new in v0.3.0. Report any issues on GitHub!
