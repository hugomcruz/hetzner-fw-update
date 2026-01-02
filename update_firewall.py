#!/usr/bin/env python3
"""
Cloudflare to Hetzner Firewall Updater

This script retrieves Cloudflare's IP ranges and updates a Hetzner Cloud firewall
to allow traffic from Cloudflare's network.
"""

import requests
import os
import sys
import logging
from typing import List, Set


# Cloudflare IP list URLs
CLOUDFLARE_IPV4_URL = "https://www.cloudflare.com/ips-v4"
CLOUDFLARE_IPV6_URL = "https://www.cloudflare.com/ips-v6"

# Hetzner Cloud API
HETZNER_API_URL = "https://api.hetzner.cloud/v1"

# Setup logging
logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO"):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def fetch_cloudflare_ips(url: str) -> Set[str]:
    """
    Fetch IP ranges from Cloudflare.
    
    Args:
        url: The URL to fetch IPs from
        
    Returns:
        Set of IP ranges (CIDR notation)
    """
    logger.debug(f"Fetching IPs from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Split by lines and strip whitespace, filter empty lines
        ips = {line.strip() for line in response.text.split('\n') if line.strip()}
        logger.debug(f"Retrieved {len(ips)} IP ranges from {url}")
        return ips
    except requests.RequestException as e:
        logger.error(f"Error fetching IPs from {url}: {e}")
        return set()


def get_hetzner_headers(api_token: str) -> dict:
    """
    Get headers for Hetzner API requests.
    
    Args:
        api_token: Hetzner Cloud API token
        
    Returns:
        Dictionary of headers
    """
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }


def get_firewall(api_token: str, firewall_id: str) -> dict:
    """
    Get firewall details from Hetzner Cloud.
    
    Args:
        api_token: Hetzner Cloud API token
        firewall_id: ID of the firewall
        
    Returns:
        Firewall details as dictionary
    """
    url = f"{HETZNER_API_URL}/firewalls/{firewall_id}"
    headers = get_hetzner_headers(api_token)
    
    logger.debug(f"Fetching firewall details for ID: {firewall_id}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.debug(f"Successfully retrieved firewall details")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching firewall: {e}")
        sys.exit(1)


def update_firewall_rules(api_token: str, firewall_id: str, ipv4_ranges: Set[str], 
                         ipv6_ranges: Set[str], ports: List[str] = None) -> bool:
    """
    Update Hetzner firewall rules with Cloudflare IP ranges.
    
    Args:
        api_token: Hetzner Cloud API token
        firewall_id: ID of the firewall to update
        ipv4_ranges: Set of IPv4 CIDR ranges
        ipv6_ranges: Set of IPv6 CIDR ranges
        ports: List of ports to allow (default: ["80", "443"])
        
    Returns:
        True if successful, False otherwise
    """
    if ports is None:
        ports = ["80", "443"]
    
    url = f"{HETZNER_API_URL}/firewalls/{firewall_id}/actions/set_rules"
    headers = get_hetzner_headers(api_token)
    
    logger.debug(f"Building firewall rules for {len(ipv4_ranges)} IPv4 and {len(ipv6_ranges)} IPv6 ranges")
    logger.debug(f"Ports to configure: {', '.join(ports)}")
    
    # Build rules for each port and protocol
    rules = []
    
    # HTTP/HTTPS rules for IPv4
    for port in ports:
        for ip in sorted(ipv4_ranges):
            rules.append({
                "direction": "in",
                "protocol": "tcp",
                "port": port,
                "source_ips": [ip],
                "description": f"Cloudflare IPv4 - Port {port}"
            })
            logger.debug(f"Added rule: IPv4 {ip} -> Port {port}")
    
    # HTTP/HTTPS rules for IPv6
    for port in ports:
        for ip in sorted(ipv6_ranges):
            rules.append({
                "direction": "in",
                "protocol": "tcp",
                "port": port,
                "source_ips": [ip],
                "description": f"Cloudflare IPv6 - Port {port}"
            })
            logger.debug(f"Added rule: IPv6 {ip} -> Port {port}")
    
    logger.debug(f"Total rules to apply: {len(rules)}")
    
    payload = {
        "rules": rules
    }
    
    logger.debug(f"Sending firewall update request to Hetzner API")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        logger.debug(f"Firewall update request successful")
        return True
    except requests.RequestException as e:
        logger.error(f"Error updating firewall: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.debug(f"Response: {e.response.text}")
        return False


def main():
    """Main function."""
    # Get log level from environment variable
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    # Get configuration from environment variables
    api_token = os.environ.get("HETZNER_API_TOKEN")
    firewall_id = os.environ.get("HETZNER_FIREWALL_ID")
    ports_str = os.environ.get("FIREWALL_PORTS", "80,443")
    
    logger.debug(f"Log level: {log_level}")
    logger.debug(f"Firewall ID: {firewall_id}")
    logger.debug(f"Ports configuration: {ports_str}")
    
    if not api_token:
        logger.error("HETZNER_API_TOKEN environment variable is required")
        sys.exit(1)
    
    if not firewall_id:
        logger.error("HETZNER_FIREWALL_ID environment variable is required")
        sys.exit(1)
    
    # Parse ports
    ports = [p.strip() for p in ports_str.split(",") if p.strip()]
    logger.debug(f"Parsed ports: {ports}")
    
    logger.debug("Starting Cloudflare IP fetch")
    ipv4_ranges = fetch_cloudflare_ips(CLOUDFLARE_IPV4_URL)
    ipv6_ranges = fetch_cloudflare_ips(CLOUDFLARE_IPV6_URL)
    
    if not ipv4_ranges and not ipv6_ranges:
        logger.error("Failed to fetch any IP ranges from Cloudflare")
        sys.exit(1)
    
    logger.info(f"Cloudflare IPs: {len(ipv4_ranges)} IPv4, {len(ipv6_ranges)} IPv6 | Updating firewall {firewall_id} | Ports: {', '.join(ports)}")
    
    logger.debug(f"Starting firewall update")
    success = update_firewall_rules(api_token, firewall_id, ipv4_ranges, ipv6_ranges, ports)
    
    if success:
        logger.info(f"✓ Firewall updated: {len(ipv4_ranges)} IPv4, {len(ipv6_ranges)} IPv6, ports {', '.join(ports)}")
    else:
        logger.error("Failed to update firewall rules")
        sys.exit(1)


if __name__ == "__main__":
    main()
