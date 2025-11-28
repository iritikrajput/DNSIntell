# 📧 MX Record Checking Features

Complete guide to email/mail server verification functionality in DNSIntel.

## Overview

DNSIntel provides comprehensive MX (Mail Exchange) record checking capabilities to help you verify email configuration for any domain.

## Features

### 1. **Basic MX Record Lookup**
Get a list of all MX records for a domain, sorted by priority.

#### CLI Usage:
```bash
dnsintel mx example.com
```

#### Python API:
```python
from dnsintel.core import dns_lookup

mx_records = dns_lookup.get_mx_records("gmail.com")
for mx in mx_records:
    print(f"Priority: {mx['priority']}, Server: {mx['exchange']}")
```

**Output Example:**
```
Found 5 MX record(s):

  1. Priority:   5 → gmail-smtp-in.l.google.com
  2. Priority:  10 → alt1.gmail-smtp-in.l.google.com
  3. Priority:  20 → alt2.gmail-smtp-in.l.google.com
  4. Priority:  30 → alt3.gmail-smtp-in.l.google.com
  5. Priority:  40 → alt4.gmail-smtp-in.l.google.com
```

---

### 2. **Full Email Configuration Check**
Check MX records along with SPF and DMARC security settings.

#### CLI Usage:
```bash
dnsintel mx example.com --full
```

#### Python API:
```python
from dnsintel.core import dns_lookup

config = dns_lookup.check_mail_configuration("example.com")
print(f"Has mail: {config['has_mail']}")
print(f"MX Records: {len(config['mx_records'])}")
print(f"SPF: {config['spf_record']}")
print(f"DMARC: {config['dmarc_record']}")
print(f"Issues: {config['issues']}")
```

**What It Checks:**
- ✅ MX records (mail servers)
- ✅ SPF record (Sender Policy Framework)
- ✅ DMARC record (Domain-based Message Authentication)
- ✅ Configuration issues and warnings

---

### 3. **DNS Lookup with MX Type**
Use the general DNS lookup command for MX records.

#### CLI Usage:
```bash
dnsintel dns example.com -t MX
dnsintel dns example.com -t ALL  # Includes MX in all records
```

#### Python API:
```python
from dnsintel.core import dns_lookup

results = dns_lookup.query_domain("example.com", "MX")
# Returns: {'domain': '...', 'records': {'MX': [...]}, 'errors': [...]}
```

---

## MX Record Priority

MX records include a **priority value**:
- **Lower numbers = Higher priority**
- Mail servers try the lowest priority first
- If that fails, they try the next highest priority

**Example:**
```
Priority  5: primary-mail.example.com     ← Tried first
Priority 10: backup-mail.example.com      ← Tried if primary fails
Priority 20: fallback-mail.example.com    ← Last resort
```

---

## Email Security Checks

### SPF (Sender Policy Framework)
Defines which mail servers can send email on behalf of your domain.

**Example SPF Record:**
```
v=spf1 include:_spf.google.com ~all
```

### DMARC (Domain-based Message Authentication)
Tells receiving mail servers what to do with emails that fail authentication.

**Example DMARC Record:**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com
```

---

## Common Use Cases

### 1. Verify Email Delivery Setup
```bash
dnsintel mx yourdomain.com --full
```
Check if your domain can receive emails.

### 2. Troubleshoot Email Issues
```bash
dnsintel mx problematic-domain.com --full
```
Identify missing SPF/DMARC records or MX configuration issues.

### 3. Compare Email Providers
```bash
dnsintel mx gmail.com
dnsintel mx outlook.com
dnsintel mx yahoo.com
```
See how different providers configure their mail servers.

### 4. Security Audit
```bash
dnsintel verify example.com
```
Comprehensive check including MX, SPF, DMARC, and more.

---

## Return Data Structure

### get_mx_records()
```python
[
    {
        "priority": 5,
        "exchange": "mail.example.com",
        "hostname": "mail.example.com"
    },
    ...
]
```

### check_mail_configuration()
```python
{
    "domain": "example.com",
    "mx_records": [...],
    "spf_record": "v=spf1 ...",
    "dmarc_record": "v=DMARC1; ...",
    "has_mail": True,
    "issues": [
        "No DMARC record found",
        ...
    ]
}
```

---

## Examples

### Check if Domain Can Receive Email
```python
from dnsintel.core import dns_lookup

config = dns_lookup.check_mail_configuration("example.com")
if config['has_mail']:
    print(f"✓ Domain can receive email at {len(config['mx_records'])} server(s)")
else:
    print("✗ Domain cannot receive email - no MX records")
```

### Find Primary Mail Server
```python
from dnsintel.core import dns_lookup

mx_records = dns_lookup.get_mx_records("example.com")
if mx_records:
    primary = mx_records[0]  # Already sorted by priority
    print(f"Primary mail server: {primary['exchange']}")
```

### Batch Check Multiple Domains
```python
from dnsintel.core import dns_lookup

domains = ["gmail.com", "yahoo.com", "outlook.com"]
for domain in domains:
    mx_records = dns_lookup.get_mx_records(domain)
    print(f"{domain}: {len(mx_records)} MX records")
```

---

## Testing

Run the included tests:
```bash
cd dnsintel-project
pytest tests/test_basic.py::TestDNSLookup::test_mx_records_structure -v
pytest tests/test_basic.py::TestDNSLookup::test_mail_configuration_structure -v
```

Run the example script:
```bash
python3 examples_mx_check.py
```

---

## Common Issues & Solutions

### ❌ "No MX records found"
**Problem:** Domain cannot receive email.

**Solutions:**
- Add MX records to your DNS configuration
- Check if domain name is spelled correctly
- Verify DNS propagation (can take up to 48 hours)

### ⚠ "No SPF record found"
**Problem:** Email may be marked as spam.

**Solution:** Add SPF TXT record to DNS:
```
v=spf1 mx ~all
```

### ⚠ "No DMARC record found"
**Problem:** Email security not configured.

**Solution:** Add DMARC TXT record at `_dmarc.yourdomain.com`:
```
v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com
```

---

## Integration Examples

### Web Application
```python
from flask import Flask, jsonify
from dnsintel.core import dns_lookup

app = Flask(__name__)

@app.route('/check-email/<domain>')
def check_email(domain):
    config = dns_lookup.check_mail_configuration(domain)
    return jsonify({
        'can_receive_email': config['has_mail'],
        'mx_count': len(config['mx_records']),
        'has_spf': config['spf_record'] is not None,
        'has_dmarc': config['dmarc_record'] is not None,
        'issues': config['issues']
    })
```

### Monitoring Script
```python
import schedule
import time
from dnsintel.core import dns_lookup

def monitor_mail_config():
    domains = ["critical-domain.com", "another-domain.com"]
    for domain in domains:
        config = dns_lookup.check_mail_configuration(domain)
        if not config['has_mail']:
            alert(f"CRITICAL: {domain} has no MX records!")
        if config['issues']:
            warn(f"Issues with {domain}: {config['issues']}")

schedule.every(1).hour.do(monitor_mail_config)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Related Commands

- `dnsintel dns <domain> -t TXT` - Check TXT records (includes SPF)
- `dnsintel verify <domain>` - Full domain security verification
- `dnsintel all <domain>` - Complete domain intelligence report

---

## Resources

- [RFC 5321 - SMTP](https://tools.ietf.org/html/rfc5321)
- [RFC 7208 - SPF](https://tools.ietf.org/html/rfc7208)
- [RFC 7489 - DMARC](https://tools.ietf.org/html/rfc7489)
- [MX Record Lookup Tool](https://mxtoolbox.com/)

---

**Need Help?** Open an issue on GitHub or consult the main README.md for more information.

