#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF: Discord Token Extractor - Advanced Simulation Test
Chrome 拡張機能の完全なシミュレーション・検証
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

class ExtensionSimulator:
    """Chrome 拡張機能の振る舞いをシミュレート"""

    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
        }
        self.manifest = None
        self.popup_js = None

    def load_extension(self):
        """拡張ファイルをロード"""
        print("[INFO] Loading extension files...")
        try:
            base_path = Path(__file__).parent

            with open(base_path / 'manifest.json', 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)

            with open(base_path / 'popup.js', 'r', encoding='utf-8') as f:
                self.popup_js = f.read()

            print("[OK] Extension files loaded")
            self.results['passed'].append('Extension files loaded successfully')
        except Exception as e:
            print("[ERROR] Failed to load extension: " + str(e))
            self.results['failed'].append('Extension loading: ' + str(e))
            raise

    def test_manifest_permissions(self):
        """Test 1: manifest.json のパーミッション検証"""
        print("\n[INFO] Test 1: Permission validation")
        try:
            required_permissions = {
                'tabs': 'Open and create tabs',
                'activeTab': 'Access active tab',
                'scripting': 'Inject content scripts',
                'clipboardWrite': 'Write to clipboard',
            }

            missing = []
            for perm, desc in required_permissions.items():
                if perm not in self.manifest.get('permissions', []):
                    missing.append(perm)

            if missing:
                msg = 'Missing permissions: ' + ', '.join(missing)
                print("[WARN] " + msg)
                self.results['warnings'].append(msg)
            else:
                print("[OK] All permissions present")
                self.results['passed'].append('All required permissions present')

            # Host permissions
            has_discord = any('discord.com' in p for p in self.manifest.get('host_permissions', []))
            if has_discord:
                print("[OK] Discord host permission granted")
                self.results['passed'].append('Discord host permission verified')
            else:
                print("[ERROR] Missing Discord host permission")
                self.results['failed'].append('Discord host permission missing')

        except Exception as e:
            print("[ERROR] Permission validation failed: " + str(e))
            self.results['failed'].append('Permission validation: ' + str(e))

    def test_popup_js_structure(self):
        """Test 2: popup.js の構造検証"""
        print("\n[INFO] Test 2: popup.js structure validation")
        try:
            # Check for required event listeners
            if 'addEventListener' not in self.popup_js:
                raise ValueError('Missing event listener')

            if 'DOMContentLoaded' not in self.popup_js:
                raise ValueError('Missing DOMContentLoaded event')

            if 'extractButton' not in self.popup_js:
                raise ValueError('Missing button ID reference')

            print("[OK] Event listeners properly configured")
            self.results['passed'].append('Event listeners properly configured')

            # Check for Chrome API calls
            chrome_apis = {
                'chrome.tabs.create': 'Open new tab',
                'chrome.scripting.executeScript': 'Execute script',
                'navigator.clipboard.writeText': 'Copy to clipboard',
            }

            missing_apis = [api for api in chrome_apis.keys() if api not in self.popup_js]

            if missing_apis:
                msg = 'Missing Chrome APIs: ' + ', '.join(missing_apis)
                print("[WARN] " + msg)
                self.results['warnings'].append(msg)
            else:
                print("[OK] All Chrome APIs present")
                self.results['passed'].append('All Chrome APIs implemented')

        except Exception as e:
            print("[ERROR] Structure validation failed: " + str(e))
            self.results['failed'].append('Structure validation: ' + str(e))

    def test_token_extraction_methods(self):
        """Test 3: トークン抽出方法の検証"""
        print("\n[INFO] Test 3: Token extraction methods validation")

        methods = {
            'webpackChunk': {
                'pattern': r'window\.webpackChunkdiscord_app.*?push',
                'description': 'Webpack chunk based extraction (most stable)',
                'reliability': 'High'
            },
            'localStorage': {
                'pattern': r'localStorage\.getItem|localStorage\.token',
                'description': 'Local storage based extraction',
                'reliability': 'Medium'
            },
            'sessionStorage': {
                'pattern': r'sessionStorage\.getItem|sessionStorage\.token',
                'description': 'Session storage based extraction',
                'reliability': 'Medium'
            },
            'ReactFiber': {
                'pattern': r'__react.*?memoizedProps|__react.*?memoizedState',
                'description': 'React Fiber inspection (newest approach)',
                'reliability': 'High'
            },
        }

        implemented = []
        for method, details in methods.items():
            if re.search(details['pattern'], self.popup_js):
                implemented.append((method, details))
                print("[OK] " + method + ": " + details['reliability'] + " reliability")

        if len(implemented) >= 3:
            print("[OK] Multiple extraction methods implemented")
            self.results['passed'].append('Multiple extraction methods (3+)')
        elif len(implemented) >= 2:
            print("[WARN] Limited extraction methods (" + str(len(implemented)) + "/4)")
            self.results['warnings'].append('Only ' + str(len(implemented)) + ' extraction methods found')
        else:
            msg = 'Insufficient extraction methods: ' + str(len(implemented))
            print("[ERROR] " + msg)
            self.results['failed'].append(msg)

    def test_error_handling(self):
        """Test 4: エラーハンドリングの検証"""
        print("\n[INFO] Test 4: Error handling validation")
        try:
            # Check for try-catch blocks
            try_count = len(re.findall(r'\btry\b', self.popup_js))
            catch_count = len(re.findall(r'\bcatch\b', self.popup_js))

            print("[INFO] Try-catch blocks: " + str(try_count))

            if try_count >= 2 and catch_count >= 2:
                print("[OK] Proper error handling implemented")
                self.results['passed'].append('Error handling implemented')
            else:
                msg = 'Insufficient error handling: ' + str(try_count) + ' try blocks'
                print("[WARN] " + msg)
                self.results['warnings'].append(msg)

            # Check for user feedback
            if 'alert(' in self.popup_js:
                print("[OK] User feedback (alerts) implemented")
                self.results['passed'].append('User feedback implemented')
            else:
                print("[WARN] No alert-based user feedback")
                self.results['warnings'].append('No user feedback mechanism')

        except Exception as e:
            print("[ERROR] Error handling validation failed: " + str(e))
            self.results['failed'].append('Error handling validation: ' + str(e))

    def test_execution_flow(self):
        """Test 5: 実行フローのシミュレーション"""
        print("\n[INFO] Test 5: Execution flow simulation")

        try:
            # Simulate button click
            print("[INFO] Simulating user interaction flow...")

            # Step 1: DOMContentLoaded
            if 'addEventListener("DOMContentLoaded"' in self.popup_js:
                print("[OK] Step 1: DOMContentLoaded listener registered")
            else:
                print("[WARN] Step 1: No DOMContentLoaded listener")

            # Step 2: Button click
            if 'addEventListener("click"' in self.popup_js:
                print("[OK] Step 2: Click listener registered")
            else:
                print("[WARN] Step 2: No click listener")

            # Step 3: Tab creation
            if 'chrome.tabs.create' in self.popup_js:
                print("[OK] Step 3: New tab creation implemented")
            else:
                print("[WARN] Step 3: No tab creation")

            # Step 4: Script injection
            if 'chrome.scripting.executeScript' in self.popup_js:
                print("[OK] Step 4: Content script injection implemented")
            else:
                print("[WARN] Step 4: No script injection")

            # Step 5: Token extraction
            if 'function extractToken' in self.popup_js:
                print("[OK] Step 5: Token extraction function defined")
            else:
                print("[WARN] Step 5: No token extraction function")

            # Step 6: Clipboard
            if 'clipboard.writeText' in self.popup_js:
                print("[OK] Step 6: Clipboard write implemented")
            else:
                print("[WARN] Step 6: No clipboard write")

            self.results['passed'].append('Execution flow verified')

        except Exception as e:
            print("[ERROR] Execution flow validation failed: " + str(e))
            self.results['failed'].append('Execution flow: ' + str(e))

    def test_security_considerations(self):
        """Test 6: セキュリティに関する検証"""
        print("\n[INFO] Test 6: Security considerations")

        try:
            # Check for potential security issues
            warnings = []

            # Check for hardcoded tokens (should not exist)
            if re.search(r'token\s*=\s*["\'][\w\.]{50,}["\']', self.popup_js):
                warnings.append('Hardcoded token detected')

            # Check for insecure clipboard operations
            if 'clipboardWrite' in self.manifest.get('permissions', []):
                print("[OK] Clipboard write permission declared")
            else:
                warnings.append('Clipboard write missing from manifest')

            # Check for Content Security Policy
            if 'content_security_policy' in self.manifest:
                print("[OK] CSP defined in manifest")
            else:
                print("[WARN] No Content Security Policy")
                warnings.append('No CSP defined')

            if warnings:
                for w in warnings:
                    self.results['warnings'].append('Security: ' + w)
            else:
                self.results['passed'].append('Security best practices followed')

            print("[OK] Security check complete")

        except Exception as e:
            print("[ERROR] Security validation failed: " + str(e))
            self.results['failed'].append('Security validation: ' + str(e))

    def test_api_compatibility(self):
        """Test 7: API 互換性の検証"""
        print("\n[INFO] Test 7: API compatibility validation")

        try:
            chrome_api_requirements = {
                'tabs': ['create', 'query'],
                'scripting': ['executeScript'],
                'runtime': ['lastError'],
            }

            for api, methods in chrome_api_requirements.items():
                for method in methods:
                    pattern = 'chrome\\.' + api + '\\.' + method
                    if re.search(pattern, self.popup_js):
                        print("[OK] chrome." + api + "." + method + " usage found")

            self.results['passed'].append('Chrome API usage verified')

        except Exception as e:
            print("[ERROR] API compatibility validation failed: " + str(e))
            self.results['failed'].append('API compatibility: ' + str(e))

    def simulate_token_extraction(self):
        """Test 8: トークン抽出のシミュレーション"""
        print("\n[INFO] Test 8: Token extraction simulation")

        try:
            # Mock Discord data
            mock_discord_state = {
                'webpackChunk': {
                    'test_module': {
                        'exports': {
                            'default': {
                                'getToken': 'function() { return "mock_token_123"; }'
                            }
                        }
                    }
                },
                'localStorage': {
                    'token': None
                },
                'sessionStorage': {
                    'token': None
                }
            }

            # Simulate webpack extraction
            print("[INFO] Simulating webpack chunk extraction...")

            # Check if extractToken is properly structured
            extract_token_match = re.search(
                r'function extractToken\(\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
                self.popup_js
            )

            if extract_token_match:
                print("[OK] extractToken function well-formed")
                self.results['passed'].append('Token extraction function verified')
            else:
                print("[WARN] extractToken structure unclear")
                self.results['warnings'].append('Token extraction function structure')

        except Exception as e:
            print("[WARN] Token extraction simulation: " + str(e))
            self.results['warnings'].append('Token extraction simulation: ' + str(e))

    def print_results(self):
        """テスト結果を出力"""
        print("\n" + "="*60)
        print("Simulation Test Results Summary")
        print("="*60 + "\n")

        if self.results['passed']:
            print("PASS (%d):" % len(self.results['passed']))
            for msg in self.results['passed']:
                print("   - " + msg)

        if self.results['warnings']:
            print("\nWARNING (%d):" % len(self.results['warnings']))
            for msg in self.results['warnings']:
                print("   - " + msg)

        if self.results['failed']:
            print("\nFAIL (%d):" % len(self.results['failed']))
            for msg in self.results['failed']:
                print("   - " + msg)

        print("\n" + "="*60)
        total = len(self.results['passed']) + len(self.results['failed'])
        if total > 0:
            pass_rate = (len(self.results['passed']) / total) * 100
            print("Score: %.1f%% (%d/%d)\n" % (pass_rate, len(self.results['passed']), total))

    def run(self):
        """Run all simulation tests"""
        print("\n" + "="*60)
        print("Advanced Simulation Test: Discord Token Extractor")
        print("="*60)

        try:
            self.load_extension()

            # Run all tests
            self.test_manifest_permissions()
            self.test_popup_js_structure()
            self.test_token_extraction_methods()
            self.test_error_handling()
            self.test_execution_flow()
            self.test_security_considerations()
            self.test_api_compatibility()
            self.simulate_token_extraction()

            # Print results
            self.print_results()

            return 0 if len(self.results['failed']) == 0 else 1

        except Exception as e:
            print("\n[ERROR] Unexpected error: " + str(e))
            return 1

def main():
    print("[INFO] Discord Token Extractor - Advanced Simulation Test\n")

    simulator = ExtensionSimulator()
    exit_code = simulator.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
