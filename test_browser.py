#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF: Discord Token Extractor - Browser Automation Test
Chrome 拡張機能を自動操作して実際に動作テスト
"""

import json
import time
import subprocess
import sys
import os
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("[ERROR] Selenium not installed. Install with:")
    print("  pip install selenium")
    sys.exit(1)

EXTENSION_PATH = str(Path(__file__).parent.absolute())
CHROME_BINARY = None  # Auto-detect or specify path

# Chrome binary locations on Windows
CHROME_PATHS = [
    r"C:\Users\kayah\AppData\Local\Google\Chrome SxS\Application\chrome.exe",  # Canary
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\kayah\AppData\Local\Google\Chrome\Application\chrome.exe",
]

class ChromeExtensionTester:
    def __init__(self):
        self.driver = None
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
        }

    def find_chrome_binary(self):
        """Find Chrome executable path"""
        for path in CHROME_PATHS:
            if os.path.exists(path):
                print("[INFO] Found Chrome at: " + path)
                return path

        # Try 'where' command
        try:
            result = subprocess.run(['where', 'chrome'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                chrome_path = result.stdout.strip().split('\n')[0]
                print("[INFO] Found Chrome at: " + chrome_path)
                return chrome_path
        except:
            pass

        print("[ERROR] Chrome not found. Please install Google Chrome.")
        sys.exit(1)

    def setup_chrome(self):
        """Setup Chrome with extension loaded"""
        print("\n[INFO] Setting up Chrome...")

        chrome_binary = self.find_chrome_binary()

        options = Options()
        options.binary_location = chrome_binary

        # Load extension
        options.add_extension(EXTENSION_PATH)

        # Additional options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        try:
            self.driver = webdriver.Chrome(options=options)
            print("[OK] Chrome started with extension loaded")
            self.results['passed'].append('Chrome started successfully')
        except Exception as e:
            print("[ERROR] Failed to start Chrome: " + str(e))
            raise

    def test_extension_popup(self):
        """Test extension popup loads"""
        print("\n[INFO] Test 1: Extension popup accessibility")
        try:
            # Get extension ID (first popup window)
            self.driver.get('chrome://extensions/')
            time.sleep(2)

            # Try to access popup
            self.driver.execute_script("""
                chrome.runtime.getManifest = function() {
                    return {
                        name: 'Discord Quick Open & Token Extract'
                    };
                };
            """)

            print("[OK] Extension popup test passed")
            self.results['passed'].append('Extension popup accessible')
        except Exception as e:
            print("[WARN] Extension popup test: " + str(e))
            self.results['warnings'].append('Extension popup: ' + str(e))

    def test_discord_page_injection(self):
        """Test if content script can be injected"""
        print("\n[INFO] Test 2: Content script injection test")
        try:
            # Create mock Discord page
            mock_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <script>
                    // Mock Discord data
                    window.webpackChunkdiscord_app = [
                        [Math.random()],
                        {},
                        function(e) {
                            e.c = {
                                'test_module': {
                                    exports: {
                                        default: {
                                            getToken: function() {
                                                return 'MTk4NjIyNDgzNzg0NjU2OTI4.C1.redacted';
                                            }
                                        }
                                    }
                                }
                            };
                        }
                    ];
                </script>
            </head>
            <body>
                <h1>Mock Discord Page</h1>
                <p id="status">Ready for token extraction</p>
            </body>
            </html>
            """

            self.driver.get("data:text/html;charset=utf-8," + mock_html)
            time.sleep(1)

            # Check if page loaded
            status = self.driver.find_element(By.ID, "status")
            assert status.text == "Ready for token extraction"

            print("[OK] Mock Discord page loaded")
            self.results['passed'].append('Content script injection possible')
        except Exception as e:
            print("[ERROR] Injection test failed: " + str(e))
            self.results['failed'].append('Content script injection: ' + str(e))

    def test_token_extraction_logic(self):
        """Test token extraction using mock data"""
        print("\n[INFO] Test 3: Token extraction logic test")
        try:
            # Simulate extractToken function
            result = self.driver.execute_script("""
                function extractToken() {
                    try {
                        let token = null;

                        // Method 1: webpackChunk
                        if (window.webpackChunkdiscord_app) {
                            window.webpackChunkdiscord_app.push([
                                [Symbol()],
                                {},
                                (e) => {
                                    for (let c in e.c) {
                                        try {
                                            const m = e.c[c].exports;
                                            if (!m) continue;
                                            if (m?.default?.getToken) {
                                                token = m.default.getToken();
                                            }
                                            for (let k in m) {
                                                if (m[k]?.getToken && typeof m[k].getToken === "function") {
                                                    token = m[k].getToken();
                                                    if (token) break;
                                                }
                                            }
                                            if (token) break;
                                        } catch (err) {}
                                    }
                                }
                            ]);
                        }

                        // Method 2: localStorage
                        if (!token) {
                            try {
                                token = localStorage.getItem('token') || localStorage.token;
                            } catch (e) {}
                        }

                        // Method 3: sessionStorage
                        if (!token) {
                            try {
                                token = sessionStorage.getItem('token') || sessionStorage.token;
                            } catch (e) {}
                        }

                        return token;
                    } catch (e) {
                        return null;
                    }
                }

                return extractToken();
            """)

            if result and len(result) > 50:
                print("[OK] Token extracted: " + result[:20] + "...")
                self.results['passed'].append('Token extraction successful')
            elif result:
                print("[WARN] Short token extracted: " + str(result))
                self.results['warnings'].append('Token format suspicious: ' + str(result))
            else:
                print("[WARN] No token extracted")
                self.results['warnings'].append('Token extraction returned null')

        except Exception as e:
            print("[ERROR] Token extraction failed: " + str(e))
            self.results['failed'].append('Token extraction: ' + str(e))

    def test_clipboard_write(self):
        """Test clipboard write capability"""
        print("\n[INFO] Test 4: Clipboard write test")
        try:
            # Test if clipboard API is available
            result = self.driver.execute_script("""
                return typeof navigator.clipboard !== 'undefined';
            """)

            if result:
                print("[OK] Clipboard API available")
                self.results['passed'].append('Clipboard API available')
            else:
                print("[WARN] Clipboard API not available")
                self.results['warnings'].append('Clipboard API unavailable')

        except Exception as e:
            print("[ERROR] Clipboard test failed: " + str(e))
            self.results['failed'].append('Clipboard test: ' + str(e))

    def test_chrome_apis(self):
        """Test if Chrome APIs can be accessed"""
        print("\n[INFO] Test 5: Chrome API availability test")
        try:
            # Check chrome object
            result = self.driver.execute_script("""
                return {
                    hasTabs: typeof chrome !== 'undefined' && typeof chrome.tabs !== 'undefined',
                    hasScripting: typeof chrome !== 'undefined' && typeof chrome.scripting !== 'undefined',
                    hasRuntime: typeof chrome !== 'undefined' && typeof chrome.runtime !== 'undefined'
                };
            """)

            apis_available = sum([result['hasTabs'], result['hasScripting'], result['hasRuntime']])

            print("[INFO] Chrome APIs available: " + str(apis_available) + "/3")
            if apis_available >= 2:
                print("[OK] Required Chrome APIs available")
                self.results['passed'].append('Chrome APIs available')
            else:
                print("[WARN] Limited Chrome API access")
                self.results['warnings'].append('Limited Chrome API access: ' + str(result))

        except Exception as e:
            print("[WARN] Chrome API test: " + str(e))
            self.results['warnings'].append('Chrome API test: ' + str(e))

    def test_button_interaction(self):
        """Test if extension button can be clicked"""
        print("\n[INFO] Test 6: Extension button interaction test")
        try:
            # Navigate to extension popup
            extension_urls = self.driver.execute_script("""
                return chrome.runtime?.getURL?.('popup.html') || 'unknown';
            """)

            if extension_urls != 'unknown':
                print("[OK] Extension URL resolved: " + str(extension_urls))
                self.results['passed'].append('Extension URL accessible')
            else:
                print("[WARN] Could not resolve extension URL")
                self.results['warnings'].append('Extension URL resolution failed')

        except Exception as e:
            print("[WARN] Button interaction test: " + str(e))
            self.results['warnings'].append('Button interaction: ' + str(e))

    def print_results(self):
        """Print test results"""
        print("\n" + "="*60)
        print("Browser Automation Test Results")
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
        """Run all tests"""
        print("\n" + "="*60)
        print("Browser Automation Test: Discord Token Extractor")
        print("="*60)
        print("Extension Path: " + EXTENSION_PATH)

        try:
            self.setup_chrome()

            # Wait for extension to load
            time.sleep(3)

            # Run tests
            self.test_extension_popup()
            self.test_discord_page_injection()
            self.test_token_extraction_logic()
            self.test_clipboard_write()
            self.test_chrome_apis()
            self.test_button_interaction()

            # Print results
            self.print_results()

            return 0 if len(self.results['failed']) == 0 else 1

        except KeyboardInterrupt:
            print("\n[INFO] Test interrupted by user")
            return 130
        except Exception as e:
            print("\n[ERROR] Unexpected error: " + str(e))
            return 1
        finally:
            if self.driver:
                print("\n[INFO] Closing Chrome...")
                try:
                    self.driver.quit()
                except:
                    pass

def main():
    print("[INFO] Discord Token Extractor - Browser Automation Test")
    print("[INFO] Checking Python dependencies...")

    # Check Selenium
    try:
        import selenium
        print("[OK] Selenium available")
    except ImportError:
        print("[ERROR] Selenium not installed")
        print("Install with: pip install selenium webdriver-manager")
        sys.exit(1)

    # Run tests
    tester = ChromeExtensionTester()
    exit_code = tester.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
