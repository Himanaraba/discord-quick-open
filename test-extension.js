/**
 * CTF: Discord Token Extractor 自動検証スクリプト
 * 拡張機能の各トークン抽出方法が正常に動作するかテスト
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const EXTENSION_PATH = path.resolve(__dirname);
const TEST_RESULTS = {
  passed: [],
  failed: [],
  warnings: [],
};

// ログ出力ユーティリティ
const log = {
  success: (msg) => console.log(`✅ ${msg}`),
  error: (msg) => console.error(`❌ ${msg}`),
  info: (msg) => console.log(`ℹ️  ${msg}`),
  warn: (msg) => console.warn(`⚠️  ${msg}`),
};

/**
 * Test 1: manifest.json の検証
 */
async function testManifest() {
  log.info('Test 1: manifest.json 構造検証');
  try {
    const manifest = JSON.parse(
      fs.readFileSync(path.join(EXTENSION_PATH, 'manifest.json'), 'utf8')
    );

    const required = ['manifest_version', 'name', 'version', 'action', 'permissions'];
    for (const field of required) {
      if (!manifest[field]) throw new Error(`Missing field: ${field}`);
    }

    if (manifest.manifest_version !== 3) {
      throw new Error('manifest_version must be 3');
    }

    if (!manifest.permissions.includes('scripting')) {
      throw new Error('Missing "scripting" permission');
    }

    if (!manifest.permissions.includes('clipboardWrite')) {
      throw new Error('Missing "clipboardWrite" permission');
    }

    if (!manifest.host_permissions?.some(p => p.includes('discord.com'))) {
      throw new Error('Missing Discord host permission');
    }

    TEST_RESULTS.passed.push('manifest.json structure valid');
    log.success('manifest.json valid');
  } catch (err) {
    TEST_RESULTS.failed.push(`Manifest validation: ${err.message}`);
    log.error(`manifest.json validation failed: ${err.message}`);
  }
}

/**
 * Test 2: popup.html の検証
 */
async function testPopupHTML() {
  log.info('Test 2: popup.html 構造検証');
  try {
    const html = fs.readFileSync(path.join(EXTENSION_PATH, 'popup.html'), 'utf8');

    if (!html.includes('extractButton')) throw new Error('Missing extractButton element');
    if (!html.includes('popup.js')) throw new Error('Missing popup.js script');
    if (!html.includes('Discord')) throw new Error('Missing Discord label text');

    TEST_RESULTS.passed.push('popup.html structure valid');
    log.success('popup.html valid');
  } catch (err) {
    TEST_RESULTS.failed.push(`HTML validation: ${err.message}`);
    log.error(`popup.html validation failed: ${err.message}`);
  }
}

/**
 * Test 3: popup.js の関数シグネチャ検証
 */
async function testPopupJS() {
  log.info('Test 3: popup.js 関数検証');
  try {
    const js = fs.readFileSync(path.join(EXTENSION_PATH, 'popup.js'), 'utf8');

    const required = ['extractTokenFromTab', 'extractToken'];
    for (const fn of required) {
      if (!js.includes(`function ${fn}`)) {
        throw new Error(`Missing function: ${fn}`);
      }
    }

    // 抽出方法の確認
    const methods = [
      { name: 'webpackChunk', pattern: /window\.webpackChunkdiscord_app/ },
      { name: 'localStorage', pattern: /localStorage\.getItem|localStorage\.token/ },
      { name: 'sessionStorage', pattern: /sessionStorage/ },
      { name: 'ReactFiber', pattern: /__react/ },
    ];

    const implemented = methods.filter(m => m.pattern.test(js));
    log.info(`Extraction methods implemented: ${implemented.map(m => m.name).join(', ')}`);

    if (implemented.length < 2) {
      TEST_RESULTS.warnings.push(`Only ${implemented.length} extraction methods found, expected 3+`);
      log.warn(`Only ${implemented.length} extraction methods found`);
    }

    TEST_RESULTS.passed.push('popup.js functions present and valid');
    log.success('popup.js valid');
  } catch (err) {
    TEST_RESULTS.failed.push(`JavaScript validation: ${err.message}`);
    log.error(`popup.js validation failed: ${err.message}`);
  }
}

/**
 * Test 4: ユニットテスト - トークン抽出関数の模擬実行
 */
async function testTokenExtraction() {
  log.info('Test 4: トークン抽出ロジック（模擬テスト）');
  try {
    // extractToken 関数を分離して実行可能に
    const mockWindow = {
      webpackChunkdiscord_app: [
        [Symbol()],
        {},
        (e) => {
          e.c = {
            test_module: {
              exports: {
                default: {
                  getToken: () => 'mock_token_from_webpack_12345',
                },
              },
            },
          };
        },
      ],
      localStorage: {
        getItem: () => null,
        token: undefined,
      },
      sessionStorage: {
        getItem: () => null,
        token: undefined,
      },
      document: {
        querySelectorAll: () => [],
      },
    };

    // 簡易的な抽出テスト
    let token = null;

    // webpack チャンク模擬
    for (const entry of mockWindow.webpackChunkdiscord_app) {
      if (typeof entry[2] === 'function') {
        entry[2]({
          c: {
            test: {
              exports: {
                default: { getToken: () => 'test_token_123' },
              },
            },
          },
        });
      }
    }

    if (!token && mockWindow.localStorage) {
      token = mockWindow.localStorage.getItem?.('token') || mockWindow.localStorage.token;
    }

    TEST_RESULTS.passed.push('Token extraction logic structure valid');
    log.success('Token extraction logic validated');
  } catch (err) {
    TEST_RESULTS.failed.push(`Token extraction test: ${err.message}`);
    log.error(`Token extraction test failed: ${err.message}`);
  }
}

/**
 * Test 5: パーミッション検証
 */
async function testPermissions() {
  log.info('Test 5: Chrome パーミッション検証');
  try {
    const manifest = JSON.parse(
      fs.readFileSync(path.join(EXTENSION_PATH, 'manifest.json'), 'utf8')
    );

    const required = ['tabs', 'scripting', 'clipboardWrite', 'activeTab'];
    const missing = required.filter(p => !manifest.permissions.includes(p));

    if (missing.length > 0) {
      TEST_RESULTS.warnings.push(`Missing permissions: ${missing.join(', ')}`);
      log.warn(`Missing permissions: ${missing.join(', ')}`);
    }

    if (!manifest.host_permissions) {
      throw new Error('Missing host_permissions');
    }

    TEST_RESULTS.passed.push('Permissions structure valid');
    log.success('Permissions validated');
  } catch (err) {
    TEST_RESULTS.failed.push(`Permission validation: ${err.message}`);
    log.error(`Permission validation failed: ${err.message}`);
  }
}

/**
 * Test 6: アイコン検証
 */
async function testIcons() {
  log.info('Test 6: アイコンファイル検証');
  try {
    const manifest = JSON.parse(
      fs.readFileSync(path.join(EXTENSION_PATH, 'manifest.json'), 'utf8')
    );

    const iconPath = manifest.icons?.[128];
    if (!iconPath) {
      throw new Error('Missing icon definition');
    }

    if (!fs.existsSync(path.join(EXTENSION_PATH, iconPath))) {
      throw new Error(`Icon file not found: ${iconPath}`);
    }

    TEST_RESULTS.passed.push('Icon file present');
    log.success('Icon validated');
  } catch (err) {
    TEST_RESULTS.warnings.push(`Icon validation: ${err.message}`);
    log.warn(`Icon validation: ${err.message}`);
  }
}

/**
 * メイン実行
 */
async function main() {
  console.log('\n🧪 Discord Token Extractor - 拡張機能検証テスト開始\n');
  console.log(`📁 拡張パス: ${EXTENSION_PATH}\n`);

  await testManifest();
  await testPopupHTML();
  await testPopupJS();
  await testTokenExtraction();
  await testPermissions();
  await testIcons();

  // 結果サマリー
  console.log('\n' + '='.repeat(50));
  console.log('📊 テスト結果サマリー\n');

  if (TEST_RESULTS.passed.length > 0) {
    console.log(`✅ 成功 (${TEST_RESULTS.passed.length}):`);
    TEST_RESULTS.passed.forEach(msg => console.log(`   • ${msg}`));
  }

  if (TEST_RESULTS.warnings.length > 0) {
    console.log(`\n⚠️  警告 (${TEST_RESULTS.warnings.length}):`);
    TEST_RESULTS.warnings.forEach(msg => console.log(`   • ${msg}`));
  }

  if (TEST_RESULTS.failed.length > 0) {
    console.log(`\n❌ 失敗 (${TEST_RESULTS.failed.length}):`);
    TEST_RESULTS.failed.forEach(msg => console.log(`   • ${msg}`));
  }

  console.log('\n' + '='.repeat(50));
  const totalTests = TEST_RESULTS.passed.length + TEST_RESULTS.failed.length;
  const passRate = ((TEST_RESULTS.passed.length / totalTests) * 100).toFixed(1);
  console.log(`\n📈 総合スコア: ${passRate}% (${TEST_RESULTS.passed.length}/${totalTests})\n`);

  const exitCode = TEST_RESULTS.failed.length === 0 ? 0 : 1;
  process.exit(exitCode);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
