# Master List Configuration

## Overview

The QR Scanner application can work with the Master List in two different configurations:

### **Option 1: Same Spreadsheet (Default)**

- **Main Spreadsheet**: Contains both attendance data and master list
- **Sheets**:
  - `Scanner` (or your chosen name) - for attendance records
  - `MasterList` - for volunteer information
- **Configuration**: Leave Master List Spreadsheet ID empty in settings

### **Option 2: Separate Spreadsheets (Recommended)**

- **Main Spreadsheet**: Contains only attendance data
- **Master List Spreadsheet**: Contains only volunteer information
- **Configuration**: Set Master List Spreadsheet ID to a different spreadsheet

## Current Issue

If you're seeing a "MasterList" sheet automatically created in your attendance monitoring spreadsheet, this means the system is currently configured to use **Option 1** (same spreadsheet).

## How to Fix

### **To Use Separate Spreadsheets (Recommended):**

1. **Create a new Google Spreadsheet** for your master list
2. **Copy the Spreadsheet ID** from the URL (the long string between `/d/` and `/edit`)
3. **Open the QR Scanner application**
4. **Go to Settings tab**
5. **Update the Master List configuration:**
   - **Master List Spreadsheet ID**: Paste your new spreadsheet ID
   - **Master List Sheet Name**: Usually "MasterList" (or your preferred name)
6. **Click "Save"** for both fields
7. **Restart the application**

### **To Keep Using Same Spreadsheet:**

If you prefer to keep everything in one spreadsheet, you can:

1. **Leave the Master List Spreadsheet ID empty** in settings
2. **The system will automatically use the main spreadsheet**
3. **The "MasterList" sheet will be created automatically** when needed

## Configuration Examples

### **Separate Spreadsheets (Recommended):**

```json
{
  "spreadsheet_id": "1PjW2-qgjWs5123qkzVyOBc-OKs2Ygk1143zkl_CymwQ",
  "sheet_name": "Scanner",
  "master_list_spreadsheet_id": "1ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZA567BCD890",
  "master_list_sheet_name": "MasterList"
}
```

### **Same Spreadsheet:**

```json
{
  "spreadsheet_id": "1PjW2-qgjWs5123qkzVyOBc-OKs2Ygk1143zkl_CymwQ",
  "sheet_name": "Scanner",
  "master_list_spreadsheet_id": "",
  "master_list_sheet_name": "MasterList"
}
```

## Benefits of Separate Spreadsheets

1. **Better Organization**: Keep attendance and master list data separate
2. **Easier Management**: Different people can manage different spreadsheets
3. **Reduced Clutter**: Main attendance sheet stays clean
4. **Better Security**: Can set different permissions for each spreadsheet
5. **Easier Backup**: Can backup master list separately

## Troubleshooting

### **"MasterList sheet created automatically"**

- This is normal if using the same spreadsheet
- To prevent this, configure separate spreadsheets as shown above

### **"Cannot find Master List"**

- Check that the Master List Spreadsheet ID is correct
- Ensure the Master List sheet name matches exactly
- Verify you have access to the master list spreadsheet

### **"Permission denied"**

- Make sure you have edit access to both spreadsheets
- Check that your Google account has the necessary permissions

## Migration

If you currently have a "MasterList" sheet in your main spreadsheet and want to move to separate spreadsheets:

1. **Export the MasterList sheet** from your main spreadsheet
2. **Create a new spreadsheet** for the master list
3. **Import the data** into the new spreadsheet
4. **Configure the QR Scanner** to use the new spreadsheet ID
5. **Delete the old MasterList sheet** from the main spreadsheet (optional)

This will give you a clean separation between attendance and master list data.
