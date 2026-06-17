#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Canary Interactive Test
Chrome Canary を起動して拡張機能を手動でテストするガイドスクリプト
"""

import subprocess
import sys
import json
from pathlib import Path
import webbrowser
import time

def get_canary_path():
    """Chrome Canary パスを取得"""
    canary_path = r"C:\Users\kayah\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
    if Path(canary_path).exists():
        return canary_path
    return None

def print_header():
    print("\n" + "="*60)
    print("Chrome Canary - Interactive Extension Test")
    print("="*60 + "\n")

def print_instructions():
    """テスト手順を表示"""
    instructions = """
[STEP 1] Chrome Canary を拡張機能ロード可能な状態で起動

    chrome-canary --load-extension=C:\\Users\\kayah\\Downloads\\aa

    または

    1. Chrome Canary を起動
    2. アドレスバーに chrome://extensions/ を入力
    3. 右上の [デベロッパーモード] をON
    4. [パッケージ化されていない拡張機能を読み込む]
    5. C:\\Users\\kayah\\Downloads\\aa を選択


[STEP 2] 拡張機能がロードされたか確認

    ✓ chrome://extensions/ ページに表示されているか
    ✓ アイコン (unlocked.png) が表示されているか
    ✓ ID が割り当てられているか（例: mjbljdfjkdjsdk...）


[STEP 3] Discord にアクセス

    https://discord.com/channels/@me

    ※ ブラウザの「すべての Cookie」を削除して fresh state でテスト推奨
    Ctrl+Shift+Delete -> Cookie と他のサイトデータ -> 削除


[STEP 4] 拡張機能ボタンをクリック

    1. Chrome のツールバー右側にアイコンが表示
    2. クリック → popup.html が表示される
    3. [Discordを開く] ボタンをクリック


[STEP 5] 結果の確認

    【初回時 - Discord にログイン済みでない場合】
    ✓ ポップアップ: "新しいタブで Discord（ホーム）を開きました"
    ✓ 新規タブで https://discord.com/channels/@me が開く
    → ログイン完了後、もう一度ボタンを押す


    【Discord ログイン済みの場合】
    ✓ ポップアップ: "トークンを抽出してクリップボードにコピーしました！"
    ✓ クリップボードに長いトークン文字列が格納される
    ✓ ブラウザコンソール (F12 → Console) にエラーがない


[STEP 6] 詳細なデバッグ（F12 開発者ツール）

    Console タブで以下を確認:

    ✓ エラーメッセージがないか
    ✓ token extraction 関連のログがないか
    ✓ "Token extraction error: ..." が表示されていないか

    Sources タブ:
    ✓ popup.js が読み込まれているか
    ✓ breakpoint を設定して関数実行を追跡


[STEP 7] Network タブでの確認

    Network タブで Chrome API 呼び出しを確認:
    ✓ chrome.tabs.create が実行されたか
    ✓ chrome.scripting.executeScript が実行されたか


[STEP 8] 複数抽出方法のテスト

    mock test page: data:text/html で以下を実行

    <script>
        // Mock Discord webpack
        window.webpackChunkdiscord_app = [
            [Symbol()],
            {},
            (e) => {
                e.c = {
                    'test': {
                        exports: {
                            default: {
                                getToken: () => 'TEST_TOKEN_' + Math.random()
                            }
                        }
                    }
                };
            }
        ];
    </script>

    このページで拡張ボタンを押して動作確認


[EXPECTED RESULTS]

    ✅ トークン抽出成功時:
       - alert: "トークンを抽出してクリップボードにコピーしました！"
       - クリップボード: MTk4NjIyNDgzNzg0NjU2OTI4... (50+ 文字)

    ⚠️ トークン未検出時:
       - alert: "トークンが見つかりませんでした..."
       - コンソール: "Token extraction error: ..."

    ⚠️ 権限不足時:
       - alert: "抽出に失敗しました..."
       - コンソール: "chrome.runtime.lastError"


[TROUBLESHOOTING]

    Q: 拡張機能が表示されない
    A: chrome://extensions/ で確認。デベロッパーモードをONにして再度読み込み

    Q: popup.html が開かない
    A: コンソールで console.log() が出力されているか確認。権限不足の可能性

    Q: "Permission denied" エラー
    A: Chrome プロファイルのセッションを削除 → 再起動

    Q: トークンが抽出されない
    A: F12 → Console で extractToken() を手動実行してデバッグ

    Q: クリップボード書き込みに失敗
    A: clipboardWrite 権限が manifest.json にあるか確認
"""
    print(instructions)

def launch_canary():
    """Chrome Canary を起動"""
    canary_path = get_canary_path()

    if not canary_path:
        print("[ERROR] Chrome Canary not found at:")
        print("  C:\\Users\\kayah\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe")
        print("[HINT] Install Chrome Canary from: https://www.google.com/chrome/canary/")
        return False

    print("[INFO] Found Chrome Canary")
    print("[INFO] Launching Chrome Canary with extension loaded...")
    print("")

    try:
        # Option 1: Load with --load-extension flag
        cmd = [
            canary_path,
            "--load-extension=C:\\Users\\kayah\\Downloads\\aa",
            "--disable-background-networking",
            "--disable-client-side-phishing-detection",
        ]

        print("[CMD] " + ' '.join(cmd[:2]))
        print("")

        # Start without blocking
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[OK] Chrome Canary launched")
        print("[INFO] Opening chrome://extensions/ for verification...")

        time.sleep(3)  # Wait for Chrome to start

        # Open extensions page in default browser
        webbrowser.open("chrome://extensions/")

        return True

    except Exception as e:
        print("[ERROR] Failed to launch Chrome Canary: " + str(e))
        return False

def main():
    print_header()

    print("[INFO] This script provides step-by-step manual testing guide")
    print("[INFO] for the Discord Token Extractor extension in Chrome Canary\n")

    # Display instructions first
    print_instructions()

    print("\n" + "="*60)
    print("Ready to launch Chrome Canary?")
    print("="*60)

    response = input("\nLaunch Chrome Canary? (y/n): ").strip().lower()

    if response == 'y' or response == 'yes':
        if launch_canary():
            print("\n[OK] Chrome Canary launched successfully")
            print("[INFO] Follow the steps above to test the extension manually")
            print("\nNote: Keep this window open for reference")
            input("\nPress Enter to continue...")
        else:
            print("\n[ERROR] Failed to launch Chrome Canary")
            return 1
    else:
        print("\n[INFO] Skipped Chrome Canary launch")
        print("[INFO] You can launch manually with:")
        print('  chrome-canary --load-extension="C:\\Users\\kayah\\Downloads\\aa"')

    return 0

if __name__ == '__main__':
    sys.exit(main())
