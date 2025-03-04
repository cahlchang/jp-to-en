# 開発者ガイド

このドキュメントは、jp-to-enの開発者向けガイドです。コントリビューションやパッケージのリリース方法について説明します。

## 環境設定

開発環境のセットアップ方法：

```bash
# リポジトリをクローン
git clone https://github.com/cahlchang/jp-to-en.git
cd jp-to-en

# 開発モードでインストール
pip install -e .
```

## テスト

テストを実行するには：

```bash
# 単体テストの実行
python -m pytest tests/
```

## コードフォーマット

コードフォーマットには[Black](https://github.com/psf/black)と[isort](https://github.com/PyCQA/isort)を使用します：

```bash
# Black でフォーマット
black jp_to_en/

# isort でインポートを整理
isort jp_to_en/
```

## パッケージのビルドとリリース

### パッケージのビルド

```bash
# ビルドツールのインストール
pip install build twine

# ソースディストリビューションとホイールのビルド
python -m build
```

これにより、`dist/`ディレクトリに以下のファイルが生成されます：
- `jp-to-en-X.Y.Z.tar.gz` (ソースディストリビューション)
- `jp_to_en-X.Y.Z-py3-none-any.whl` (ホイール)

### TestPyPIでのテスト

本番のPyPIにアップロードする前に、TestPyPIでテストすることをお勧めします：

```bash
# TestPyPIにアップロード
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# TestPyPIからのインストールテスト
pip install --index-url https://test.pypi.org/simple/ --no-deps jp-to-en
```

### PyPIへのアップロード

```bash
# PyPIにアップロード
twine upload dist/*
```

アップロード時にPyPIのユーザー名とパスワードを求められます。APIトークンを使用することも可能です。

## バージョニング

このプロジェクトでは[セマンティックバージョニング](https://semver.org/)を採用しています：

- **メジャーバージョン**: 後方互換性を破壊する変更
- **マイナーバージョン**: 後方互換性を維持した機能追加
- **パッチバージョン**: 後方互換性を維持したバグ修正

バージョンを更新する際は、以下のファイルを修正します：
- `setup.py`: `version`パラメータ
- `jp_to_en/__init__.py`: `__version__`変数

## リリースチェックリスト

新しいバージョンをリリースする前に、以下を確認してください：

1. すべてのテストがパスすること
2. バージョン番号が更新されていること
3. CHANGELOGが更新されていること
4. ドキュメントが最新であること
5. GitHubリリースノートが準備されていること

## コントリビューションガイドライン

1. バグ報告や機能リクエストは、GitHub Issuesで行ってください
2. プルリクエストは、新しいブランチで作成してください
3. すべてのコードは、テストとドキュメントを含める必要があります
4. コミットメッセージは明確で説明的にしてください
