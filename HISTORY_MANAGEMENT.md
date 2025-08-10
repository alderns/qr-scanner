# Scan History Management

## Overview

The QR Scanner application now uses an improved scan history management system that prevents file accumulation and provides better maintainability.

## Key Features

### 1. Single File Approach

- **Current History**: `scan_history_current.json` - Contains all current session data
- **Archive Files**: `scan_history_archive_YYYYMMDD_HHMMSS.json` - Archived history files
- **No More Timestamped Files**: Eliminates the creation of hundreds of timestamped files

### 2. Automatic Cleanup

- **File Limit**: Maximum 10 history files kept
- **Age Limit**: Files older than 7 days are automatically removed
- **Duplicate Prevention**: Removes duplicate entries based on timestamp and scan data

### 3. Smart Saving

- **Change Detection**: Only saves when there are actual changes to the history
- **Reduced Frequency**: Auto-save interval increased from 30 seconds to 5 minutes
- **Efficient Storage**: Prevents unnecessary file writes

## File Structure

```
data/
├── scan_history_current.json          # Current session history
├── scan_history_archive_20250725_191642.json  # Archived history
├── user_config.json                   # Application configuration
└── exports/                           # Export directory
```

## Maintenance

### Manual Cleanup

If you need to manually clean up history files:

```bash
python cleanup_history.py
```

This script will:

1. Consolidate all existing history files into a single current file
2. Remove duplicate entries
3. Archive the most recent file
4. Delete all other timestamped files

### Automatic Cleanup

The application automatically:

- Cleans up old files when saving new data
- Archives current history on application shutdown
- Maintains a maximum of 10 history files

## Configuration

### Auto-Save Interval

- **Default**: 5 minutes (300 seconds)
- **Location**: `src/config/settings.py`
- **Configurable**: Can be adjusted in user settings

### File Limits

- **Max Files**: 10 history files
- **Max Age**: 7 days
- **Location**: `src/utils/file_utils.py` in `_cleanup_old_history_files()`

## Benefits

1. **Reduced File Count**: From hundreds of files to just a few
2. **Better Performance**: Faster file operations and reduced disk usage
3. **Easier Maintenance**: Simple file structure and automatic cleanup
4. **Data Integrity**: Duplicate prevention and proper archiving
5. **User-Friendly**: No manual intervention required

## Troubleshooting

### If History Files Accumulate Again

1. Run the cleanup script: `python cleanup_history.py`
2. Check if the application is properly shutting down
3. Verify auto-save settings are appropriate

### If Data Loss Occurs

1. Check for archive files in the data directory
2. Look for `scan_history_archive_*.json` files
3. Restore from the most recent archive if needed

## Migration

The new system is backward compatible. Existing timestamped files will be automatically consolidated when the application starts or when the cleanup script is run.
