# Chrome Canary での手動テストガイド

Chrome Canary が起動済みです。以下の手順でテストしてください。

---

## 🚀 クイックスタート

### Step 1: 拡張がロードされているか確認

Chrome Canary で以下のアドレスにアクセス:

```
chrome://extensions/
```

**確認項目:**
- ✅ "Discord Quick Open & Token Extract" が表示されている
- ✅ デベロッパーモード（右上）が ON になっている
- ✅ 拡張の ID が割り当てられている（例: `abcdefghijklmnop...`）
- ✅ アイコン（鍵マーク）が表示されている

---

## 🧪 テスト実行

### Test A: ポップアップ表示テスト

1. Chrome のツールバー右上（拡張アイコン）をクリック
2. ポップアップが表示されるか確認

**期待結果:**
```
┌─────────────────────────┐
│  Discord Quick Open...  │
│                         │
│   [Discordを開く]       │
│                         │
│  Discordを新しいタブ... │
└─────────────────────────┘
```

---

### Test B: Discord にログイン（初回）

**【パターン1: まだ Discord にログインしていない場合】**

1. 拡張ボタンを押す → `[Discordを開く]` をクリック
2. Discord ホームが新規タブで開く
3. メッセージが表示される:
   ```
   ✅ 新しいタブで Discord（ホーム）を開きました。
   
   ログイン完了後、もう一度ボタンを押すと
   トークンを抽出できます。
   ```

4. Discord にメールアドレス・パスワードでログイン

**確認:**
- ✅ https://discord.com/channels/@me に遷移
- ✅ ポップアップが自動で閉じた

---

### Test C: トークン抽出テスト（重要）

**【パターン2: Discord にログイン済みの場合】**

1. Chrome ツールバーで拡張ボタンをクリック
2. `[Discordを開く]` をクリック

**期待結果:**

```
✅ トークンを抽出してクリップボードにコピーしました！
```

**確認方法:**

#### クリップボード内容の確認
```
Ctrl + V  （テキストエディタに貼り付け）
```

**トークンの形式:**
```
MTk4NjIyNDgzNzg0NjU2OTI4.Clwa7A.ZZrCx_eiNYezERClStW4xAb1K3k
```

- 最初の部分: `MTk4...` （Base64）
- 中央の区切り: `.`
- 最後: `...xAb1K3k`
- **最小長: 50 文字以上**

#### ブラウザコンソール確認
```
F12 を押す → Console タブ
```

**確認項目:**
- ✅ エラーメッセージがない
- ✅ "Token extraction error" がない
- ✅ 赤いエラーアイコンがない（❌）

---

## 🔍 詳細なデバッグ（F12）

### Sources タブでの確認

1. `F12` → `Sources` タブ
2. 左パネルで以下を確認:
   - `popup.js`
   - `popup.html`
   - Content script の実行

### Network タブでの確認

1. `F12` → `Network` タブ
2. 拡張ボタンをクリック
3. 以下の API 呼び出しが出現:
   - `chrome.tabs.create` → 新規タブ作成
   - `chrome.scripting.executeScript` → スクリプト注入

### Console タブでエラー確認

```javascript
// コンソールで手動実行してデバッグ可能:
window.extractToken  // 関数の確認
```

---

## ✅ テストケース別の期待結果

### Case 1: 正常系（トークン抽出成功）

| 操作 | 期待結果 |
|---|---|
| 拡張ボタンをクリック | popup 表示 |
| `[Discordを開く]` を押す | alert: "トークン抽出成功" |
| Ctrl+V でペースト | トークンが貼り付き |
| F12 → Console | エラーなし |

**スコア:** ✅ 100%

---

### Case 2: トークン未検出

| 操作 | 期待結果 |
|---|---|
| 拡張ボタンをクリック | popup 表示 |
| `[Discordを開く]` を押す（非 Discord ページから） | alert: "トークンが見つかりませんでした" |
| 再度試す（Discord ページで） | 同じメッセージ または 成功 |

**スコア:** ⚠️ 部分成功

---

### Case 3: 権限不足

| 操作 | 期待結果 |
|---|---|
| 拡張ボタンをクリック | popup 表示 |
| `[Discordを開く]` を押す | alert: "抽出に失敗しました" |
| F12 → Console | `chrome.runtime.lastError` 表示 |

**スコア:** ❌ 失敗（権限設定を確認）

---

## 🛠️ トラブルシューティング

### Q1: 拡張が表示されない

**A:** `chrome://extensions/` で確認

```
✓ デベロッパーモードが ON
✓ "Discord Quick Open..." が一覧に表示
✓ 有効 (青スライダー) になっている
```

**復帰方法:**
```
1. デベロッパーモード OFF/ON を切り替え
2. 拡張を無効 → 再度有効
3. Chrome Canary を再起動
```

---

### Q2: popup.html が開かない

**A:** コンソールエラー確認

```
F12 → Console
```

**よくある原因:**
- manifest.json の `default_popup` パスが間違っている
- popup.js の読み込み失敗
- 権限不足

**確認コマンド:**
```javascript
chrome.runtime.lastError  // エラーメッセージ表示
```

---

### Q3: "Permission denied" エラー

**A:** Chrome プロファイルをリセット

```powershell
# Chrome Canary をすべて閉じる
Get-Process chrome | Stop-Process -Force

# プロファイルをリセット
Remove-Item "$env:LOCALAPPDATA\Google\Chrome SxS\User Data" -Recurse -Force

# 再起動
.\launch_canary.ps1
```

---

### Q4: トークンが抽出されない

**A:** 4つの抽出方法を順番にテスト

1. **webpack chunk 方法:**
   ```javascript
   // Console で実行
   window.webpackChunkdiscord_app  // 存在確認
   ```

2. **localStorage 方法:**
   ```javascript
   localStorage.getItem('token')  // 確認
   localStorage.token             // 確認
   ```

3. **sessionStorage 方法:**
   ```javascript
   sessionStorage.getItem('token')
   ```

4. **ReactFiber 方法:**
   ```javascript
   Object.keys(document.body).filter(k => k.startsWith('__react'))
   ```

---

### Q5: クリップボード書き込みに失敗

**A:** 権限確認

```json
// manifest.json の確認
{
  "permissions": [
    "clipboardWrite"  // ← この行が必須
  ]
}
```

**復帰方法:**
```
1. manifest.json を編集
2. clipboardWrite を追加
3. chrome://extensions/ で拡張をリロード
4. 再テスト
```

---

## 📊 テスト結果の記録

### チェックリスト

- [ ] 拡張が `chrome://extensions/` に表示
- [ ] popup.html がクリック時に開く
- [ ] `[Discordを開く]` ボタンが反応
- [ ] 新規タブで Discord が開く
- [ ] トークン抽出メッセージが表示
- [ ] クリップボードにトークンが格納
- [ ] F12 Console にエラーなし
- [ ] 複数回試行でも成功

### スコア計算

```
スコア = (成功した確認項目数 / 8) × 100%

8/8 = 100% ✅
7/8 = 87.5% ⚠️
6/8 = 75% ⚠️
```

---

## 📝 報告テンプレート

テスト完了時に以下を報告してください:

```
【テスト環境】
- Chrome Canary バージョン: _____
- 拡張 ID: _____
- Discord ログイン状態: ✅ / ❌

【テスト結果】
✓ 拡張読み込み: 成功
✓ popup 表示: 成功
✓ トークン抽出: 成功 / 失敗
✓ クリップボード: 成功 / 失敗

【抽出されたトークン形式】
MTk4... (最初の20文字)

【エラーメッセージ】
(F12 Console から)

【総合スコア】
8/8 (100%)
```

---

## 🔗 参考資料

- Chrome Extensions Manifest V3: https://developer.chrome.com/docs/extensions/mv3/
- Selenium Documentation: https://selenium-python.readthedocs.io/
- Discord Architecture: https://discord.com/

---

**テスト日時:** 2026-06-18  
**テスト環境:** Windows 11, Chrome Canary, Python 3.12  
**ステータス:** 🟢 実施可能
