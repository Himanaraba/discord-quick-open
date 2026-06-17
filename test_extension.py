#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF: Discord Token Extractor Extension Validation
Automated tests for token extraction methods
"""

import json
import os
import re
import sys
from pathlib import Path

# Test Results
TEST_RESULTS = {
    'passed': [],
    'failed': [],
    'warnings': [],
}

def log_success(msg):
    print("[OK] " + msg)

def log_error(msg):
    print("[NG] " + msg)

def log_warn(msg):
    print("[WARN] " + msg)

def log_info(msg):
    print("[INFO] " + msg)

# ============================================
# Test 1: manifest.json validation
# ============================================
def test_manifest():
    log_info('Test 1: manifest.json structure validation')
    try:
        manifest_path = Path(__file__).parent / 'manifest.json'
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        required = ['manifest_version', 'name', 'version', 'action', 'permissions']
        for field in required:
            if field not in manifest:
                raise ValueError("Missing field: " + field)

        if manifest['manifest_version'] != 3:
            raise ValueError("manifest_version must be 3")

        if 'scripting' not in manifest['permissions']:
            raise ValueError('Missing "scripting" permission')

        if 'clipboardWrite' not in manifest['permissions']:
            raise ValueError('Missing "clipboardWrite" permission')

        if 'host_permissions' not in manifest or \
           not any('discord.com' in p for p in manifest.get('host_permissions', [])):
            raise ValueError('Missing Discord host permission')

        TEST_RESULTS['passed'].append('manifest.json structure valid')
        log_success('manifest.json valid')
    except Exception as e:
        TEST_RESULTS['failed'].append("Manifest validation: " + str(e))
        log_error("manifest.json validation failed: " + str(e))

# ============================================
# Test 2: popup.html validation
# ============================================
def test_popup_html():
    log_info('Test 2: popup.html structure validation')
    try:
        html_path = Path(__file__).parent / 'popup.html'
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        if 'extractButton' not in html:
            raise ValueError('Missing extractButton element')
        if 'popup.js' not in html:
            raise ValueError('Missing popup.js script')
        if 'Discord' not in html and 'discord' not in html:
            raise ValueError('Missing Discord label text')

        TEST_RESULTS['passed'].append('popup.html structure valid')
        log_success('popup.html valid')
    except Exception as e:
        TEST_RESULTS['failed'].append("HTML validation: " + str(e))
        log_error("popup.html validation failed: " + str(e))

# ============================================
# Test 3: popup.js function validation
# ============================================
def test_popup_js():
    log_info('Test 3: popup.js function validation')
    try:
        js_path = Path(__file__).parent / 'popup.js'
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        required = ['extractTokenFromTab', 'extractToken']
        for fn in required:
            if ('function ' + fn) not in js:
                raise ValueError("Missing function: " + fn)

        methods = [
            ('webpackChunk', r'window\.webpackChunkdiscord_app'),
            ('localStorage', r'localStorage\.getItem|localStorage\.token'),
            ('sessionStorage', r'sessionStorage'),
            ('ReactFiber', r'__react'),
        ]

        implemented = [name for name, pattern in methods if re.search(pattern, js)]
        log_info("Extraction methods: " + ', '.join(implemented))

        if len(implemented) < 2:
            TEST_RESULTS['warnings'].append("Only " + str(len(implemented)) + " extraction methods found")
            log_warn("Only " + str(len(implemented)) + " extraction methods found")

        TEST_RESULTS['passed'].append('popup.js functions present and valid')
        log_success('popup.js valid')
    except Exception as e:
        TEST_RESULTS['failed'].append("JavaScript validation: " + str(e))
        log_error("popup.js validation failed: " + str(e))

# ============================================
# Test 4: Token extraction logic test
# ============================================
def test_token_extraction():
    log_info('Test 4: Token extraction logic validation')
    try:
        js_path = Path(__file__).parent / 'popup.js'
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        if 'function extractToken()' not in js:
            raise ValueError("extractToken function not found")

        if 'try' not in js or 'catch' not in js:
            raise ValueError("Error handling not implemented")

        patterns = [
            (r'webpackChunkdiscord_app.*?push', 'webpack chunk method'),
            (r'localStorage\.getItem', 'localStorage method'),
            (r'sessionStorage', 'sessionStorage method'),
        ]

        found = [desc for pattern, desc in patterns if re.search(pattern, js)]
        if len(found) < 2:
            raise ValueError("Too few extraction methods: " + str(found))

        TEST_RESULTS['passed'].append('Token extraction logic valid')
        log_success('Token extraction logic validated')
    except Exception as e:
        TEST_RESULTS['failed'].append("Token extraction test: " + str(e))
        log_error("Token extraction test failed: " + str(e))

# ============================================
# Test 5: Permission validation
# ============================================
def test_permissions():
    log_info('Test 5: Chrome permission validation')
    try:
        manifest_path = Path(__file__).parent / 'manifest.json'
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        required = ['tabs', 'scripting', 'clipboardWrite', 'activeTab']
        perms = manifest.get('permissions', [])
        missing = [p for p in required if p not in perms]

        if missing:
            TEST_RESULTS['warnings'].append("Missing permissions: " + ', '.join(missing))
            log_warn("Missing permissions: " + ', '.join(missing))

        if 'host_permissions' not in manifest:
            raise ValueError('Missing host_permissions')

        TEST_RESULTS['passed'].append('Permissions structure valid')
        log_success('Permissions validated')
    except Exception as e:
        TEST_RESULTS['failed'].append("Permission validation: " + str(e))
        log_error("Permission validation failed: " + str(e))

# ============================================
# Test 6: Icon validation
# ============================================
def test_icons():
    log_info('Test 6: Icon file validation')
    try:
        manifest_path = Path(__file__).parent / 'manifest.json'
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        icons = manifest.get('icons', {})
        if not icons or '128' not in icons:
            raise ValueError('Missing icon definition')

        icon_path = Path(__file__).parent / icons['128']
        if not icon_path.exists():
            raise ValueError("Icon file not found: " + icons['128'])

        TEST_RESULTS['passed'].append('Icon file present')
        log_success('Icon validated')
    except Exception as e:
        TEST_RESULTS['warnings'].append("Icon validation: " + str(e))
        log_warn("Icon validation: " + str(e))

# ============================================
# Test 7: JavaScript syntax check
# ============================================
def test_js_syntax():
    log_info('Test 7: JavaScript syntax validation')
    try:
        js_path = Path(__file__).parent / 'popup.js'
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        if js.count('{') != js.count('}'):
            raise ValueError("Mismatched braces")
        if js.count('(') != js.count(')'):
            raise ValueError("Mismatched parentheses")

        if 'chrome.tabs.create' not in js:
            raise ValueError("Missing chrome.tabs.create call")
        if 'chrome.scripting.executeScript' not in js:
            raise ValueError("Missing chrome.scripting.executeScript call")
        if 'navigator.clipboard.writeText' not in js:
            raise ValueError("Missing clipboard write functionality")

        TEST_RESULTS['passed'].append('JavaScript syntax valid')
        log_success('JavaScript syntax valid')
    except Exception as e:
        TEST_RESULTS['failed'].append("JS syntax: " + str(e))
        log_error("JS syntax check failed: " + str(e))

# ============================================
# Test 8: File integrity
# ============================================
def test_file_integrity():
    log_info('Test 8: File integrity validation')
    try:
        base_path = Path(__file__).parent
        required_files = [
            'manifest.json',
            'popup.html',
            'popup.js',
            'unlocked.png',
        ]

        missing = [f for f in required_files if not (base_path / f).exists()]
        if missing:
            raise ValueError("Missing files: " + ', '.join(missing))

        TEST_RESULTS['passed'].append('All required files present')
        log_success('File integrity valid')
    except Exception as e:
        TEST_RESULTS['failed'].append("File integrity: " + str(e))
        log_error("File integrity check failed: " + str(e))

# ============================================
# Main execution
# ============================================
def main():
    print('\n' + '='*60)
    print('Test: Discord Token Extractor Extension Validation')
    print('='*60 + '\n')

    # Run all tests
    test_manifest()
    test_popup_html()
    test_popup_js()
    test_token_extraction()
    test_permissions()
    test_icons()
    test_js_syntax()
    test_file_integrity()

    # Summary
    print('\n' + '='*60)
    print('Test Results Summary\n')

    if TEST_RESULTS['passed']:
        print('PASS (%d):' % len(TEST_RESULTS['passed']))
        for msg in TEST_RESULTS['passed']:
            print('   - ' + msg)

    if TEST_RESULTS['warnings']:
        print('\nWARNING (%d):' % len(TEST_RESULTS['warnings']))
        for msg in TEST_RESULTS['warnings']:
            print('   - ' + msg)

    if TEST_RESULTS['failed']:
        print('\nFAIL (%d):' % len(TEST_RESULTS['failed']))
        for msg in TEST_RESULTS['failed']:
            print('   - ' + msg)

    print('\n' + '='*60)
    total_tests = len(TEST_RESULTS['passed']) + len(TEST_RESULTS['failed'])
    if total_tests > 0:
        pass_rate = (len(TEST_RESULTS['passed']) / total_tests) * 100
        print('\nScore: %.1f%% (%d/%d)\n' % (pass_rate, len(TEST_RESULTS['passed']), total_tests))
    else:
        print('\nNo tests executed\n')

    return 0 if len(TEST_RESULTS['failed']) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
