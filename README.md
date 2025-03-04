# jp-to-en

日本語のコードコメントを英語に変換するCLIツール

## 概要

`jp-to-en`は、プログラムファイル内の日本語コメントを検出し、文脈を考慮して自然な英語に変換するコマンドラインツールです。OpenAIのtranslateモデルを使用して高品質な翻訳を提供します。

## 特徴

- 様々なプログラミング言語のコメント形式に対応
- 日本語テキストの自動検出
- 文脈を考慮した自然な英語への変換
- 変換前後の差分プレビュー
- バッチ処理による複数ファイルの一括処理
- OpenAI APIを活用した高品質な翻訳

## インストール

### 前提条件

- Python 3.9以上
- OpenAI APIキー

### pipを使用したインストール

以下のいずれかの方法でインストールできます：

#### 1. PyPIからインストール (推奨)

```bash
# pipでインストール
pip install jp-to-en

# コマンドとして実行
jp-to-en --help
```

#### 2. GitHubからインストール

```bash
# GitHubから直接インストール
pip install git+https://github.com/cahlchang/jp-to-en.git

# コマンドとして実行
jp-to-en --help
```

#### 3. ソースからインストール

```bash
# リポジトリのクローン
git clone https://github.com/cahlchang/jp-to-en.git
cd jp-to-en

# 依存関係のインストール
pip install .

# または開発モードでインストール（編集可能モード）
pip install -e .

# コマンドとして実行
jp-to-en --help
```

## 使用方法

### 基本的な使い方

```bash
# 単一ファイルの処理
jp-to-en path/to/file.py

# ディレクトリ内のすべてのファイルを処理
jp-to-en path/to/directory

# 再帰的にディレクトリを処理（-rオプション）
jp-to-en path/to/directory -r

# カレントディレクトリ内のファイルを処理（パス省略時）
jp-to-en

# カレントディレクトリ以下を再帰的に処理
jp-to-en -r

# 変更をプレビューするだけで実際には変更しない
jp-to-en path/to/file.py --dry-run
```

### OpenAI APIキーの設定

APIキーは以下のいずれかの方法で指定できます：

1. コマンドライン引数で指定:
   ```bash
   jp-to-en path/to/file.py --api-key sk-your-api-key
   ```

2. 環境変数で指定:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key
   jp-to-en path/to/file.py
   ```

3. APIキーを保存して再利用:
   ```bash
   # APIキーを保存する（初回のみ）
   jp-to-en path/to/file.py --api-key sk-your-api-key --save-api-key
   
   # 以降は保存されたAPIキーを自動的に使用
   jp-to-en path/to/file.py
   ```

   APIキーは `~/.jp-to-en/credentials.json` に保存されます。

### OpenAI APIキーの取得方法

APIキーを持っていない場合は、以下の手順で取得できます：

1. [OpenAI APIキー管理ページ](https://platform.openai.com/api-keys)にアクセス
2. OpenAIアカウントでログイン（アカウントがない場合は作成）
3. 「Create new secret key」ボタンをクリック
4. キーに名前を付け、作成されたAPIキーをコピー

**注意**: APIキーは表示されるのは一度だけです。安全な場所に保管するか、`--save-api-key`オプションを使って保存してください。

### pyenv環境での使用方法

pyenv環境で`jp-to-en`コマンドが見つからない場合は、[pyenv_installation_guide.md](pyenv_installation_guide.md)を参照してください。主な解決方法：

1. `pyenv global 3.12.1` - jp-to-enがインストールされているPythonバージョンをグローバルに設定
2. `pyenv local 3.12.1` - プロジェクトディレクトリ内のみでそのバージョンを使用
3. 現在のPython環境に直接インストール: `pip install jp-to-en`
4. 仮想環境を作成してその中にインストール

### 詳細オプション

```
usage: jp-to-en [-h] [--recursive] [--output-dir OUTPUT_DIR] [--dry-run] [--verbose]
                 [--quiet] [--api-key API_KEY] [--config CONFIG]
                 paths [paths ...]

Convert Japanese comments in code to English

positional arguments:
  paths                 Files or directories to process

options:
  -h, --help            show this help message and exit
  --recursive, -r       Process directories recursively
  --output-dir, -o OUTPUT_DIR
                        Directory to write output files (if not specified, files are modified in-place)
  --dry-run, -d         Show changes without modifying files
  --verbose, -v         Enable verbose output
  --quiet, -q           Suppress all output except errors
  --api-key, -k API_KEY
                        OpenAI API key (can also be set via OPENAI_API_KEY environment variable)
  --config, -c CONFIG   Path to configuration file
```

## サポートされている言語

現在、以下のプログラミング言語のコメントがサポートされています：

- Python (`.py`, `.pyi`)
- その他の言語は近日対応予定

## アーキテクチャ

このツールは、以下のモジュールで構成されています：

- **パーサー**: 各プログラミング言語のコメントを抽出
- **検出器**: テキスト内の日本語を検出
- **翻訳器**: OpenAI APIを使用して日本語テキストを英語に翻訳
- **フォーマッター**: 変換結果を表示・出力

## 貢献

バグ報告や機能リクエストは、GitHub Issuesにてお願いします。プルリクエストも歓迎します。

## ライセンス

[MIT License](LICENSE)
