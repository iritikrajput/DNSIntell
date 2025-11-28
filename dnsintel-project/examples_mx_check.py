#!/usr/bin/env python3
"""
Example script demonstrating MX record checking functionality.

This shows various ways to check email configuration for domains.
"""

from dnsintel.core import dns_lookup
from dnsintel.utils.output import print_header, print_success, print_info, print_warning


def check_single_domain(domain):
    """Check MX records for a single domain."""
    print_header(f"Checking MX Records for: {domain}")
    
    # Get MX records
    mx_records = dns_lookup.get_mx_records(domain)
    
    if mx_records:
        print_success(f"✓ Found {len(mx_records)} MX record(s):\n")
        for i, mx in enumerate(mx_records, 1):
            print_info(f"  {i}. Priority: {mx['priority']:3d} → {mx['exchange']}")
    else:
        print_warning("⚠ No MX records found - email may not be configured\n")


def check_full_email_config(domain):
    """Check complete email configuration including SPF and DMARC."""
    print_header(f"Full Email Configuration for: {domain}")
    
    config = dns_lookup.check_mail_configuration(domain)
    
    # MX Records
    print_success("MX Records:")
    if config['mx_records']:
        for mx in config['mx_records']:
            print_info(f"  Priority {mx['priority']:3d}: {mx['exchange']}")
    else:
        print_warning("  None found")
    
    # SPF
    print_success("\nSPF Record:")
    if config['spf_record']:
        print_info(f"  {config['spf_record']}")
    else:
        print_warning("  Not configured")
    
    # DMARC
    print_success("\nDMARC Record:")
    if config['dmarc_record']:
        print_info(f"  {config['dmarc_record']}")
    else:
        print_warning("  Not configured")
    
    # Issues
    if config['issues']:
        print_warning("\nConfiguration Issues:")
        for issue in config['issues']:
            print_warning(f"  • {issue}")
    else:
        print_success("\n✓ Email configuration looks good!")
    
    print()


def compare_domains(domains):
    """Compare MX records across multiple domains."""
    print_header("Comparing MX Records Across Domains")
    
    for domain in domains:
        mx_records = dns_lookup.get_mx_records(domain)
        print_info(f"\n{domain}:")
        if mx_records:
            print_success(f"  ✓ {len(mx_records)} MX record(s)")
            for mx in mx_records:
                print_info(f"    Priority {mx['priority']:3d}: {mx['exchange']}")
        else:
            print_warning("  ⚠ No MX records")


if __name__ == "__main__":
    # Example 1: Check a single domain
    check_single_domain("gmail.com")
    
    # Example 2: Full email configuration check
    check_full_email_config("google.com")
    
    # Example 3: Compare multiple domains
    domains_to_compare = [
        "gmail.com",
        "outlook.com",
        "yahoo.com",
    ]
    compare_domains(domains_to_compare)
    
    # Example 4: Using the standard DNS lookup with MX type
    print_header("Using Standard DNS Lookup for MX Records")
    results = dns_lookup.query_domain("gmail.com", "MX")
    dns_lookup.display_results(results, "MX")

