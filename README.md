# QR Code Scanner with Google Sheets Integration

A modern, feature-rich QR code scanner application with Google Sheets integration, built with Python and Tkinter.

## Features

- **Real-time QR Code Scanning**: Live camera feed with instant QR code detection
- **Google Sheets Integration**: Automatically save scan data to Google Sheets
- **Master List Support**: Load and search reference data from Google Sheets
- **Modern GUI**: Clean, intuitive interface with tabbed layout
- **Scan History**: View and export scan history
- **QR Scanner Simulation**: Simulate real QR scanner behavior (typing + Enter)
- **Clipboard Integration**: Copy scan data to clipboard
- **Export Functionality**: Export scan history to CSV/TXT files

## Project Structure

```
qr/
├── src/
│   ├── config/           # Configuration files
│   │   ├── paths.py      # File path management
│   │   ├── settings.py   # Application settings
│   │   └── theme.py      # UI theme configuration
│   ├── core/             # Core application logic
│   │   ├── app_manager.py      # Main application coordinator
│   │   ├── camera_manager.py   # Camera and scanning logic
│   │   ├── sheets_manager.py   # Google Sheets integration
│   │   └── scan_processor.py   # Scan data processing
│   ├── gui/              # GUI components
│   │   ├── components.py       # Reusable UI components
│   │   └── main_window.py      # Main application window
│   └── utils/            # Utility functions
│       ├── file_utils.py       # File operations
│       ├── logger.py           # Logging functionality
│       ├── scanner_utils.py    # QR scanner simulation
│       └── validation.py       # Data validation
├── assets/               # Static assets (icons, styles)
├── docs/                 # Documentation
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd qr
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install optional dependencies** (for enhanced features):

   ```bash
   python install_optional_deps.py
   ```

   Or install manually:

   ```bash
   pip install psutil  # For enhanced performance monitoring
   ```

4. **Setup Google Sheets API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the `credentials.json` file
   - Place it in the project root directory

## Usage

1. **Start the application**:

   ```bash
   python main.py
   ```

2. **Setup Google Sheets**:

   - Go to the "Settings" tab
   - Click "Setup Credentials" and select your `credentials.json` file
   - Enter your Google Spreadsheet ID and sheet name
   - Click "Connect to Sheets"

3. **Start Scanning**:
   - Go to the "Scanner" tab
   - Click "Start Camera" to begin scanning
   - Point your camera at QR codes to scan them
   - Scanned data will automatically be saved to Google Sheets

## Configuration

### Google Sheets Setup

1. **Create a Google Spreadsheet** with the following structure:

   - Sheet 1: "QR_Scans" (for scan data)
   - Sheet 2: "MasterList" (for reference data)

2. **Share the spreadsheet** with your Google account

3. **Get the Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

### Application Settings

Edit `src/config/settings.py` to customize:

- Window size and title
- Default spreadsheet settings
- Typing simulation parameters
- Notification settings

## Features in Detail

### QR Code Scanning

- Supports multiple barcode formats (QR, Code128, EAN, etc.)
- Real-time video feed with 30 FPS
- Duplicate scan prevention
- Automatic data validation

### Google Sheets Integration

- Automatic sheet creation if missing
- Real-time data synchronization
- Master list loading and searching
- Error handling and retry logic

### GUI Features

- Modern, responsive design
- Tabbed interface for organization
- Status indicators for all components
- Keyboard shortcuts and hotkeys
- Dark theme support

### Data Management

- Scan history with timestamps
- Export to CSV/TXT formats
- Clipboard integration
- Data validation and sanitization

## Development

### Running Tests

```bash
pytest src/tests/
```

### Code Style

The project follows PEP 8 guidelines. Use a code formatter like `black` for consistent formatting.

### Adding New Features

1. Follow the existing module structure
2. Add appropriate logging
3. Update documentation
4. Add tests for new functionality

## Troubleshooting

### Common Issues

1. **Camera not working**:

   - Ensure camera is not in use by another application
   - Check camera permissions
   - Try different camera index (0, 1, 2)

2. **Google Sheets connection issues**:

   - Verify credentials.json is correct
   - Check spreadsheet sharing permissions
   - Ensure Google Sheets API is enabled

3. **Import errors**:
   - Install all required dependencies
   - Check Python version (3.7+ required)
   - Verify file paths and permissions

### Logs

Check the application logs for detailed error information. Logs are stored in the `logs/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the troubleshooting section above

# qr-scanner
