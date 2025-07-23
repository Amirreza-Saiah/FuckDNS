# FuckDNS

FuckDNS is a Python-based tool designed for Windows users to test, manage, and configure DNS servers for the Wi-Fi interface. It allows users to test DNS servers against a specified URL, apply DNS configurations, and manage custom DNS entries through a user-friendly GUI built with Tkinter. The tool is particularly useful for testing DNS servers to bypass restrictions or improve connectivity for specific websites, such as those commonly blocked in certain regions (e.g., Android development repositories).

## Features

- Test DNS Servers: Test multiple DNS servers by sending HTTP requests to a user-specified URL and display the HTTP status code (e.g., 200, 403, 404) for each server.
- Apply DNS Configurations: Set primary and secondary DNS servers for the Wi-Fi interface manually or automatically (first DNS with status code 200).
- Clear DNS Settings: Reset DNS settings to DHCP with a single click.
- Add Custom DNS: Add and save custom DNS configurations for future use.
- URL History: Save and reuse previously tested URLs, with default suggestions for restricted Android development repositories.
- Real-Time Status: Display the current DNS configuration (e.g., DHCP or specific DNS servers) at the top of the interface.
- Asynchronous Testing: Test DNS servers without freezing the UI, showing "Testing..." for each server during the process.
- DNS Cache Flushing: Automatically flush the DNS cache after setting or clearing DNS to ensure accurate results.

## Installation

### Prerequisites
- Python 3.7 or higher (includes `tkinter`, `json`, `os`, `dataclasses`, `subprocess`, `ctypes`, `sys`, `asyncio`, `threading`, and `winreg`).
- Windows operating system (required for `winreg` and `netsh` commands).

### Dependencies
The following third-party Python packages are required:
- `requests`
- `aiohttp`

Install them using the provided `requirements.txt`:
```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:
```
aiohttp==3.8.6
requests==2.31.0
```

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/FuckDNS.git
   cd FuckDNS
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python FuckDNS.py
   ```

**Note**: The tool requires administrative privileges to modify DNS settings. It will prompt for elevation (UAC) if not run as administrator.

## Usage

1. Launch the Application: Run `FuckDNS.py`. The GUI will open, displaying a list of preconfigured DNS servers and the current DNS status (e.g., "Current DNS: DHCP" or "Current DNS: Shecan (178.22.122.100, 185.51.200.2)").
2. Select or Enter a URL: Choose a URL from the dropdown (includes defaults like `https://developer.android.com`) or enter a custom URL to test DNS servers against.
3. Test DNS Servers:
   - Click **Test DNS** to test all DNS servers asynchronously. The status column will show "Testing..." during the process, followed by the HTTP status code (e.g., "200", "403", "Failed").
   - Click **Apply First 200 DNS** to test DNS servers and automatically apply the first one that returns a 200 status code, stopping further tests.
4. Apply DNS: Select a DNS configuration from the list and click **Apply Selected DNS** to set it for the Wi-Fi interface.
5. Clear DNS: Click **Clear DNS** to reset the Wi-Fi interface to DHCP.
6. Add Custom DNS: Click **Add DNS** to open a window where you can enter a new DNS configuration (name, primary DNS, secondary DNS, and optional comment). Saved configurations persist across sessions.
7. View Current DNS: The top label shows the current DNS configuration, updated after every apply or clear action.

## Screenshots

*To be added: Include screenshots of the GUI, showing the DNS list, URL selection, and status updates.*

## Configuration Files

- **dns_config.json**: Stores custom DNS configurations added by the user.
- **url_history.json**: Saves the history of URLs tested by the user.

Both files are created automatically in the same directory as the script when you add a custom DNS or test a new URL.

## Preconfigured DNS Servers

The tool includes the following DNS servers by default:
- Shecan: 178.22.122.100, 185.51.200.2
- Begzar: 185.55.226.26, 185.55.225.25
- Radar Game: 10.202.10.10, 10.202.10.11
- Electrot: 78.157.42.100, 78.157.42.101
- 403 DNS: 10.202.10.202, 10.202.10.102 [In Memories]
- Sheltertm: 94.103.125.157, 94.103.125.158
- Beshkanapp: 181.41.194.177, 181.41.194.186
- Pishgaman: 5.202.100.100, 5.202.100.101
- Shatel: 85.15.1.14, 85.15.1.15 [Shatel ADSL Only]
- Level3: 209.244.0.3, 209.244.0.4
- Cloudflare: 1.1.1.1, 1.0.0.1
- Google DNS: 8.8.8.8, 4.2.2.4

## Default URLs

The tool includes default URLs for testing, focusing on Android development repositories that may be restricted in some regions:
- https://developer.android.com
- https://repo.maven.apache.org
- https://jcenter.bintray.com
- https://dl.google.com

## Notes

- **Administrative Privileges**: The tool uses `netsh` commands to modify DNS settings, which require administrator rights. It automatically prompts for elevation if needed.
- **DNS Cache**: The tool flushes the DNS cache (`ipconfig /flushdns`) after every DNS change to ensure accurate test results.
- **Asynchronous Testing**: DNS tests are performed asynchronously using `aiohttp` to prevent the GUI from freezing, with real-time status updates.
- **Error Handling**: The tool handles errors gracefully, displaying "Failed" for DNS servers that encounter issues during testing or configuration.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Built with Python and Tkinter for a lightweight, cross-compatible GUI.
- Uses `aiohttp` for asynchronous HTTP requests and `requests` for synchronous operations.
- Designed for Windows users needing to bypass DNS restrictions or test connectivity.
