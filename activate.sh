#!/bin/bash
# Quick activation script for DomainIntel

cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ DomainIntel virtual environment activated!"
echo ""
echo "Available commands:"
echo "  domainintel mx <domain>           - Check MX records"
echo "  domainintel mx <domain> --full    - Full email config"
echo "  domainintel dns <domain> -t MX    - DNS lookup for MX"
echo "  domainintel whois <domain>        - WHOIS lookup"
echo "  domainintel ssl <domain>          - SSL check"
echo "  domainintel verify <domain>       - Full verification"
echo "  domainintel all <domain>          - Complete report"
echo ""
echo "Try: domainintel mx google.com --full"
echo ""
