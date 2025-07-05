# uithub_expander

[uithub.com](https://uithub.com)から取得したリポジトリ構造テキストを
実際のディレクトリ構造に展開するPythonツール。

## 🚀 概要

uithub.comはGitHubリポジトリの構造をテキスト形式で出力するサービスですが、
このツールを使えばそのテキストを実際のファイルシステムに復元できます。

## 📦 インストール

```bash
# 開発版をインストール
git clone https://github.com/your-username/uithub_expander.git
cd uithub_expander
pip install -e .

# または直接実行
python -m uithub_expander
```

## 🛠️ 使用方法

### コマンドライン

```bash
# 基本的な使用方法
python -m uithub_expander uithub.txt

# 出力ディレクトリを指定
python -m uithub_expander uithub.txt -o my_project

# 絶対パスで出力先を指定
python -m uithub_expander uithub.txt --output-dir ./extracted
```

### Python API

```python
from uithub_expander import UithubExpander

# 基本的な使用方法
expander = UithubExpander("uithub.txt", "output_dir")
expander.extract()

# カスタム出力ディレクトリ
expander = UithubExpander("uithub.txt", "./my_project")
expander.extract()
```

## 📋 入力ファイル形式

uithub.comから取得したテキストファイルは以下の形式である必要があります：

```text
├── README.md
├── src/
│   ├── main.py
│   └── utils.py
└── tests/
    └── test_main.py

/README.md:
----------------------------------------
 1 | # My Project
 2 |
 3 | This is a sample project.

/src/main.py:
----------------------------------------
 1 | def main():
 2 |     print("Hello, World!")
 3 |
 4 | if __name__ == "__main__":
 5 |     main()
```

## 🔧 機能

- **自動ディレクトリ作成**: ファイルパスに基づいて必要なディレクトリを自動生成
- **行番号除去**: uithub.comの行番号形式（`1 | `）を自動的に除去
- **UTF-8対応**: 日本語などのマルチバイト文字を完全サポート
- **セキュリティ対策**: ディレクトリトラバーサル攻撃を防止
- **詳細ログ**: 処理状況をリアルタイムで表示

## 🏗️ アーキテクチャ

### 主要クラス

- `UithubExpander`: メインクラス
  - `parse_file()`: 入力ファイルの解析
  - `_extract_file_contents()`: ファイル内容の抽出
  - `_extract_tree_structure()`: ツリー構造の抽出
  - `create_directory_structure()`: ディレクトリ構造の作成
  - `extract()`: メイン処理の実行

### 処理フロー

1. **ファイル読み込み**: UTF-8エンコーディングで入力ファイルを読み込み
2. **内容解析**: 正規表現でファイルパスと内容を分離
3. **行番号除去**: 各行から行番号部分を除去
4. **ディレクトリ作成**: パスに基づいてディレクトリ構造を作成
5. **ファイル作成**: クリーンアップされた内容でファイルを作成

## 🧪 開発環境

### 必要条件

- Python 3.13+
- uv (パッケージマネージャー)

### 開発セットアップ

```bash
# 依存関係のインストール
uv sync

# テストの実行
uv run pytest

# 型チェック
uv run mypy src/

# リンター
uv run ruff check src/
uv run ruff format src/
```

### 開発ツール

- **mypy**: 静的型チェック
- **pytest**: テストフレームワーク
- **ruff**: リンター・フォーマッター
- **sphinx**: ドキュメント生成

## 📝 ライセンス

MIT License

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 🔍 トラブルシューティング

### よくあるエラー

**FileNotFoundError**: 入力ファイルが存在しない

```bash
# 解決策: ファイルパスを確認
ls -la uithub.txt
```

**UnicodeDecodeError**: ファイルエンコーディングがUTF-8でない

```bash
# 解決策: ファイルをUTF-8に変換
iconv -f SHIFT_JIS -t UTF-8 uithub.txt > uithub_utf8.txt
```

**ValueError**: ファイル内容のパターンが見つからない

```bash
# 解決策: ファイル形式を確認
head -20 uithub.txt
```
