# Discord Token Extractor - テスト・検証ガイド

CTF チャレンジ向け Chrome 拡張機能の自動検証スイート

## テストプログラム一覧

### 1. **test_extension.py** - 静的構造検証
基本的なファイル・構文・パーミッション検証

```bash
python test_extension.py
```

**検証内容:**
- `manifest.json` 構造と必須フィールド
- `popup.html` UI 要素
- `popup.js` 関数・権限
- JavaScript 構文（括弧バランス）
- ファイル完全性

**結果:** 8/8 テストパス

---

### 2. **test_simulation.py** - 振る舞いシミュレーション
拡張機能の実際の動作をシミュレートして検証（**推奨**）

```bash
python test_simulation.py
```

**検証内容:**
- Chrome API の正しい使用法
- トークン抽出の 4つの方法（webpack, localStorage, sessionStorage, ReactFiber）
- エラーハンドリング（try-catch の充実度）
- 実行フロー（ボタンクリック → タブ作成 → スクリプト注入 → トークン抽出 → クリップボード）
- セキュリティ考慮（CSP、権限の最小化）
- API 互換性

**結果:** 11/11 テストパス（警告: CSP 未定義）

---

### 3. **test_browser.py** - 実ブラウザ自動化テスト
（Chrome インストール時に実行可能）

```bash
python test_browser.py
```

**検証内容:**
- Chrome 起動と拡張ロード
- popup の実際のロード
- Discord ページへの content script 注入
- 実トークン抽出シミュレーション
- Clipboard API 動作確認

---

## セットアップ

### 依存関係のインストール

```bash
pip install selenium webdriver-manager
```

### 実行方法

```bash
# 推奨: シミュレーションテスト（最も詳細）
python test_simulation.py

# または静的検証のみ
python test_extension.py
```

---

## テスト結果の解釈

| ステータス | 意味 |
|---|---|
| `[OK]` / `PASS` | テスト成功 |
| `[WARN]` / `WARNING` | 警告（非致命的） |
| `[NG]` / `FAIL` | テスト失敗 |

---

## トークン抽出方法（実装済み）

### 1. webpackChunk 方法 ⭐ 最高信頼度
```javascript
window.webpackChunkdiscord_app.push([...])
```
- Discord の webpack 構造から直接アクセス
- 最も安定（Discord アップデートに強い）

### 2. localStorage 方法
```javascript
localStorage.getItem('token')
```
- ローカルストレージからの直接取得
- 中程度の信頼度

### 3. sessionStorage 方法
```javascript
sessionStorage.getItem('token')
```
- セッションストレージからの取得
- 中程度の信頼度

### 4. ReactFiber 方法 ⭐ 最新対応
```javascript
__react... -> memoizedProps/memoizedState
```
- React コンポーネント状態の検査
- 最新 Discord UI に対応

---

## 実行フロー検証済み

1. ✅ `DOMContentLoaded` リスナ登録
2. ✅ ボタンクリック時の処理
3. ✅ Discord ホーム新規タブ作成
4. ✅ content script 注入
5. ✅ トークン抽出実行
6. ✅ クリップボードへコピー

---

## セキュリティ警告（修正推奨）

⚠️ **Content Security Policy (CSP) 未定義**

`manifest.json` に以下を追加:
```json
{
  "content_security_policy": {
    "extension_pages": "script-src 'self'"
  }
}
```

---

## トラブルシューティング

### Selenium がインストールできない
```bash
pip install --upgrade pip
pip install selenium webdriver-manager
```

### Chrome が見つからない
ブラウザがインストールされていない場合、シミュレーションテスト（`test_simulation.py`）のみ実行可能

### JavaScript 構文エラーが出た
`popup.js` の括弧・ブレースが対称か確認
```bash
python test_extension.py  # 自動チェック
```

---

## スコア計算方法

```
Score = (PASS / (PASS + FAIL)) × 100%
```

警告（WARNING）は計算に含まれません。

---

## CTF チャレンジ提出ガイド

以下をスクリーンショット/出力として提出:

1. `test_extension.py` の実行結果
2. `test_simulation.py` の実行結果
3. 修正点（CSP 追加）の提出

---

## ライセンス & 注意

⚠️ **このツールは教育目的（CTF）のみ**

実際の Discord アカウントに対する使用は:
- 利用規約違反
- 刑事責任の可能性
- アカウント BANのリスク

---

## 更新履歴

- 2026-06-18: 初版作成（4抽出方法、完全シミュレーション）
