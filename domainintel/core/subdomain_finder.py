"""
Subdomain finder functionality using multiple techniques.
"""

import concurrent.futures
import dns.resolver
import requests
from typing import Dict, Any, List, Set, Optional
import json
import os

from domainintel.utils.output import print_info, print_success, print_error, print_warning


# Common subdomains wordlist (built-in)
COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
    "ns3", "ns4", "dns", "dns1", "dns2", "mx", "mx1", "mx2", "email", "cloud",
    "api", "dev", "stage", "staging", "test", "testing", "prod", "production",
    "app", "apps", "admin", "administrator", "portal", "dashboard", "panel",
    "cpanel", "whm", "webdisk", "autodiscover", "autoconfig", "secure", "ssl",
    "vpn", "remote", "gateway", "gw", "proxy", "cdn", "static", "assets",
    "images", "img", "media", "files", "download", "downloads", "upload",
    "uploads", "backup", "backups", "db", "database", "mysql", "postgres",
    "sql", "oracle", "mongo", "redis", "cache", "memcached", "elasticsearch",
    "search", "web", "www1", "www2", "www3", "web1", "web2", "server", "server1",
    "server2", "host", "node", "node1", "node2", "cluster", "lb", "load",
    "balancer", "haproxy", "nginx", "apache", "iis", "blog", "forum", "wiki",
    "docs", "doc", "help", "support", "ticket", "tickets", "helpdesk", "status",
    "monitor", "monitoring", "grafana", "kibana", "prometheus", "zabbix",
    "nagios", "jenkins", "ci", "cd", "gitlab", "github", "bitbucket", "git",
    "svn", "repo", "repository", "jira", "confluence", "slack", "chat",
    "irc", "meet", "meeting", "zoom", "teams", "video", "stream", "streaming",
    "live", "rtmp", "hls", "uat", "qa", "demo", "sandbox", "beta", "alpha",
    "internal", "intranet", "extranet", "corp", "corporate", "staff", "employee",
    "hr", "payroll", "finance", "accounting", "sales", "marketing", "crm",
    "erp", "sap", "oracle", "shop", "store", "ecommerce", "cart", "checkout",
    "payment", "pay", "billing", "invoice", "order", "orders", "tracking",
    "ship", "shipping", "mobile", "m", "wap", "android", "ios", "iphone",
    "calendar", "cal", "time", "ntp", "ldap", "ad", "active", "directory",
    "sso", "auth", "login", "signin", "signup", "register", "account",
    "accounts", "profile", "user", "users", "member", "members", "customer",
    "clients", "partner", "partners", "affiliate", "affiliates", "reseller",
    "agent", "agents", "dealer", "dealers", "vendor", "vendors", "supplier",
    "exchange", "owa", "outlook", "office", "office365", "o365", "sharepoint",
    "onedrive", "skype", "lync", "ocs", "sip", "voip", "pbx", "asterisk",
    "freeswitch", "sbc", "edge", "fw", "firewall", "ids", "ips", "waf",
    "dmz", "bastion", "jump", "ssh", "sftp", "rsync", "nfs", "smb", "cifs",
    "nas", "san", "storage", "s3", "minio", "swift", "ceph", "gluster",
    "hadoop", "spark", "kafka", "rabbitmq", "activemq", "zeromq", "queue",
    "worker", "job", "jobs", "task", "tasks", "cron", "scheduler", "airflow",
    "luigi", "celery", "flower", "beat", "health", "healthcheck", "ping",
    "pong", "echo", "trace", "debug", "log", "logs", "logging", "syslog",
    "splunk", "elk", "logstash", "fluentd", "graylog", "papertrail", "sentry",
    "bugsnag", "rollbar", "newrelic", "datadog", "appdynamics", "dynatrace",
]


def get_subdomains_from_crtsh(domain: str, timeout: int = 30) -> Set[str]:
    """
    Get subdomains from Certificate Transparency logs via crt.sh.

    Args:
        domain: Domain name to search
        timeout: Request timeout in seconds

    Returns:
        Set of discovered subdomains
    """
    subdomains = set()
    
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            try:
                data = response.json()
                for entry in data:
                    name = entry.get("name_value", "")
                    # Handle wildcard and multi-line entries
                    for sub in name.split("\n"):
                        sub = sub.strip().lower()
                        if sub.startswith("*."):
                            sub = sub[2:]
                        if sub.endswith(f".{domain}") or sub == domain:
                            if sub != domain:
                                subdomains.add(sub)
            except json.JSONDecodeError:
                pass
    except requests.RequestException:
        pass
    
    return subdomains


def resolve_subdomain(subdomain: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to resolve a subdomain and get its IP addresses.

    Args:
        subdomain: Full subdomain to resolve

    Returns:
        Dictionary with subdomain info if resolved, None otherwise
    """
    result = {
        "subdomain": subdomain,
        "ips": [],
        "cname": None
    }
    
    try:
        # Try A record
        answers = dns.resolver.resolve(subdomain, "A")
        result["ips"] = [str(rdata) for rdata in answers]
        return result
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.Timeout:
        return None
    except Exception:
        pass
    
    # Try CNAME record
    try:
        answers = dns.resolver.resolve(subdomain, "CNAME")
        result["cname"] = str(answers[0])
        return result
    except Exception:
        pass
    
    return None


def bruteforce_subdomains(
    domain: str,
    wordlist: List[str] = None,
    threads: int = 10
) -> List[Dict[str, Any]]:
    """
    Bruteforce subdomains using a wordlist.

    Args:
        domain: Domain name to check
        wordlist: List of subdomain prefixes to try
        threads: Number of concurrent threads

    Returns:
        List of discovered subdomains with their IP addresses
    """
    if wordlist is None:
        wordlist = COMMON_SUBDOMAINS
    
    discovered = []
    subdomains_to_check = [f"{prefix}.{domain}" for prefix in wordlist]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(resolve_subdomain, sub): sub 
            for sub in subdomains_to_check
        }
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                discovered.append(result)
    
    return discovered


def find_subdomains(
    domain: str,
    use_crtsh: bool = True,
    use_bruteforce: bool = True,
    wordlist: List[str] = None,
    threads: int = 10,
    resolve: bool = True
) -> Dict[str, Any]:
    """
    Find subdomains using multiple techniques.

    Args:
        domain: Domain name to search
        use_crtsh: Use Certificate Transparency logs
        use_bruteforce: Use DNS bruteforcing
        wordlist: Custom wordlist for bruteforcing
        threads: Number of concurrent threads
        resolve: Resolve discovered subdomains to IPs

    Returns:
        Dictionary containing discovery results
    """
    results = {
        "domain": domain,
        "subdomains": [],
        "total_found": 0,
        "sources": {
            "crtsh": 0,
            "bruteforce": 0
        },
        "errors": []
    }
    
    all_subdomains = set()
    resolved_subdomains = []
    
    # Certificate Transparency logs
    if use_crtsh:
        try:
            crtsh_subs = get_subdomains_from_crtsh(domain)
            results["sources"]["crtsh"] = len(crtsh_subs)
            all_subdomains.update(crtsh_subs)
        except Exception as e:
            results["errors"].append(f"crt.sh error: {str(e)}")
    
    # DNS Bruteforcing
    if use_bruteforce:
        try:
            brute_results = bruteforce_subdomains(domain, wordlist, threads)
            for item in brute_results:
                subdomain = item["subdomain"]
                if subdomain not in all_subdomains:
                    results["sources"]["bruteforce"] += 1
                all_subdomains.add(subdomain)
                resolved_subdomains.append(item)
        except Exception as e:
            results["errors"].append(f"Bruteforce error: {str(e)}")
    
    # Resolve remaining subdomains from crt.sh
    if resolve and use_crtsh:
        crtsh_only = all_subdomains - {r["subdomain"] for r in resolved_subdomains}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(resolve_subdomain, sub): sub 
                for sub in crtsh_only
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    resolved_subdomains.append(result)
    
    # Sort by subdomain name
    resolved_subdomains.sort(key=lambda x: x["subdomain"])
    
    results["subdomains"] = resolved_subdomains
    results["total_found"] = len(resolved_subdomains)
    
    return results


def load_wordlist(filepath: str) -> List[str]:
    """
    Load a wordlist from a file.

    Args:
        filepath: Path to wordlist file

    Returns:
        List of subdomain prefixes
    """
    wordlist = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    wordlist.append(line)
    except FileNotFoundError:
        pass
    
    return wordlist


def display_results(results: Dict[str, Any], verbose: bool = False) -> None:
    """
    Display subdomain finder results.

    Args:
        results: Dictionary containing discovery results
        verbose: Show detailed information
    """
    domain = results.get("domain")
    subdomains = results.get("subdomains", [])
    total = results.get("total_found", 0)
    sources = results.get("sources", {})
    errors = results.get("errors", [])
    
    print_success(f"\nSubdomain Discovery Results for {domain}")
    print_info(f"\nTotal subdomains found: {total}")
    
    # Source breakdown
    print_info("\nDiscovery sources:")
    print_info(f"  • Certificate Transparency (crt.sh): {sources.get('crtsh', 0)}")
    print_info(f"  • DNS Bruteforce: {sources.get('bruteforce', 0)}")
    
    if not subdomains:
        print_warning("\nNo subdomains discovered.")
        return
    
    print_success("\nDiscovered Subdomains:")
    print_info("-" * 70)
    
    for item in subdomains:
        subdomain = item.get("subdomain", "")
        ips = item.get("ips", [])
        cname = item.get("cname")
        
        if verbose:
            print_success(f"\n  {subdomain}")
            if ips:
                for ip in ips:
                    print_info(f"    └─ A: {ip}")
            if cname:
                print_info(f"    └─ CNAME: {cname}")
        else:
            if ips:
                ip_str = ", ".join(ips[:3])
                if len(ips) > 3:
                    ip_str += f" (+{len(ips)-3} more)"
                print_info(f"  {subdomain:<40} → {ip_str}")
            elif cname:
                print_info(f"  {subdomain:<40} → CNAME: {cname}")
            else:
                print_info(f"  {subdomain}")
    
    print_info("-" * 70)
    
    # Display errors if any
    if errors:
        print_warning("\nWarnings:")
        for error in errors:
            print_warning(f"  {error}")
    
    # Tips
    print_info(f"\nTip: Use 'domainintel subdomains {domain} -v' for detailed output")
    print_info(f"     Use 'domainintel subdomains {domain} --wordlist <file>' for custom wordlist")

