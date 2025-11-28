# 📧 Quick Start: MX Record Checking

## Installation

```bash
cd dnsintel-project
pip install -e .
```

## CLI Commands (3 Ways)

### Method 1: Dedicated MX Command (Recommended)
```bash
# Quick MX check
dnsintel mx gmail.com

# Full email configuration
dnsintel mx gmail.com --full
```

### Method 2: DNS Command with MX Type
```bash
# MX records only
dnsintel dns gmail.com -t MX

# All DNS records (includes MX)
dnsintel dns gmail.com -t ALL
```

### Method 3: Comprehensive Verification
```bash
# Includes MX in full domain check
dnsintel verify gmail.com
dnsintel all gmail.com
```

## Python API (3 Ways)

### Method 1: Get MX Records Only
```python
from dnsintel.core import dns_lookup

mx_records = dns_lookup.get_mx_records("gmail.com")
for mx in mx_records:
    print(f"{mx['priority']}: {mx['exchange']}")
```

### Method 2: Full Email Configuration
```python
from dnsintel.core import dns_lookup

config = dns_lookup.check_mail_configuration("gmail.com")
print(f"MX Records: {config['mx_records']}")
print(f"SPF: {config['spf_record']}")
print(f"DMARC: {config['dmarc_record']}")
print(f"Issues: {config['issues']}")
```

### Method 3: General DNS Query
```python
from dnsintel.core import dns_lookup

results = dns_lookup.query_domain("gmail.com", "MX")
mx_records = results['records'].get('MX', [])
```

## Real-World Examples

### Check Your Domain
```bash
dnsintel mx yourdomain.com --full
```

### Verify Email Setup
```python
from dnsintel.core import dns_lookup

domain = "yourdomain.com"
config = dns_lookup.check_mail_configuration(domain)

if not config['has_mail']:
    print("❌ No MX records - email won't work!")
elif not config['spf_record']:
    print("⚠️  No SPF - email may be marked as spam")
elif not config['dmarc_record']:
    print("⚠️  No DMARC - email security not configured")
else:
    print("✅ Email configuration looks good!")
```

### Compare Providers
```bash
dnsintel mx gmail.com
dnsintel mx outlook.com
dnsintel mx yahoo.com
```

## What You Get

### Output Format
```
MX Records Check: gmail.com
============================================================

Found 5 MX record(s):

  1. Priority:   5 → gmail-smtp-in.l.google.com
  2. Priority:  10 → alt1.gmail-smtp-in.l.google.com
  3. Priority:  20 → alt2.gmail-smtp-in.l.google.com
  4. Priority:  30 → alt3.gmail-smtp-in.l.google.com
  5. Priority:  40 → alt4.gmail-smtp-in.l.google.com

  Tip: Use 'dnsintel mx gmail.com --full' for complete email configuration
```

### Full Configuration Output
```
MX Records Check: gmail.com
============================================================

MX Records Found:
  1. Priority:   5 → gmail-smtp-in.l.google.com
  2. Priority:  10 → alt1.gmail-smtp-in.l.google.com
  ...

SPF Record:
  v=spf1 include:_spf.google.com ~all

DMARC Record:
  v=DMARC1; p=none; rua=mailto:mailauth-reports@google.com

✓ Email configuration looks good!
```

## Try It Now!

```bash
# Test with a known domain
dnsintel mx google.com --full

# Or run the example script
python3 examples_mx_check.py
```

## Next Steps

- Read [MX_FEATURES.md](MX_FEATURES.md) for detailed documentation
- Check [README.md](README.md) for complete DNSIntel features
- Run tests: `pytest tests/test_basic.py -v`

---

**Happy MX checking! 🚀**

