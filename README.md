# Cloudflare to Hetzner Firewall Updater

This script automatically retrieves Cloudflare's IP ranges and updates a Hetzner Cloud firewall to allow traffic from Cloudflare's network.

## Features

- Fetches the latest Cloudflare IPv4 and IPv6 ranges
- Updates Hetzner Cloud firewall rules via API
- Configurable ports (default: 80, 443)
- Error handling and validation

## Prerequisites

- Python 3.6+
- Hetzner Cloud API token
- Hetzner Cloud firewall ID

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `HETZNER_API_TOKEN`: Your Hetzner Cloud API token (required)
- `HETZNER_FIREWALL_ID`: The ID of your Hetzner firewall (required)
- `FIREWALL_PORTS`: Comma-separated list of ports to allow (optional, default: "80,443")

### Getting your Hetzner API Token

1. Log in to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select your project
3. Go to "Security" → "API Tokens"
4. Click "Generate API Token"
5. Give it a name and select "Read & Write" permissions
6. Copy the token (you won't be able to see it again)

### Getting your Firewall ID

1. In Hetzner Cloud Console, go to "Firewalls"
2. Click on your firewall
3. The ID is in the URL: `https://console.hetzner.cloud/projects/[PROJECT_ID]/firewalls/[FIREWALL_ID]`

Or use the API:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  https://api.hetzner.cloud/v1/firewalls
```

## Usage

### Basic usage:
```bash
export HETZNER_API_TOKEN="your-api-token-here"
export HETZNER_FIREWALL_ID="your-firewall-id-here"

python update_firewall.py
```

### Custom ports:
```bash
export HETZNER_API_TOKEN="your-api-token-here"
export HETZNER_FIREWALL_ID="your-firewall-id-here"
export FIREWALL_PORTS="80,443,8080,8443"

python update_firewall.py
```

### Using a .env file:
Create a `.env` file:
```
HETZNER_API_TOKEN=your-api-token-here
HETZNER_FIREWALL_ID=your-firewall-id-here
FIREWALL_PORTS=80,443
```

Then run:
```bash
source .env
python update_firewall.py
```

## Automation

You can automate this script to run periodically using cron:

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 3 AM
0 3 * * * cd /path/to/script && /usr/bin/python3 update_firewall.py
```

Or use systemd timer on Linux systems.

## How It Works

1. Fetches Cloudflare's IPv4 ranges from: `https://www.cloudflare.com/ips-v4`
2. Fetches Cloudflare's IPv6 ranges from: `https://www.cloudflare.com/ips-v6`
3. Creates firewall rules for each IP range and specified port
4. Updates the Hetzner firewall via the Hetzner Cloud API

## Security Notes

- **Never commit your API token to version control**
- Store sensitive credentials in environment variables or a secrets manager
- Use API tokens with minimal required permissions
- Regularly rotate your API tokens
- Consider using Hetzner's API token expiration features

## Troubleshooting

### "Error: HETZNER_API_TOKEN environment variable is required"
Make sure you've exported the environment variable before running the script.

### "Error fetching firewall: 404"
Check that your firewall ID is correct. You can list all firewalls with:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  https://api.hetzner.cloud/v1/firewalls
```

### "Error updating firewall: 401"
Your API token may be invalid or expired. Generate a new one from the Hetzner Cloud Console.

## License

MIT
