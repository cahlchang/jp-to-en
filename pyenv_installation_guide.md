# pyenv環境でのjp-to-enの使用方法

pyenv環境でjp-to-enを使用する際のガイドです。以下のいずれかの方法で解決できます：

## 方法1: グローバルPythonバージョンを変更する

jp-to-enがインストールされているPythonバージョン（3.12.1）をグローバルで使用するように設定します：

```bash
# 3.12.1をグローバルPythonとして設定
pyenv global 3.12.1

# 確認
python --version  # Python 3.12.1と表示されるはず
jp-to-en --help   # ヘルプが表示されるはず
```

## 方法2: プロジェクト固有のPythonバージョンを設定する

特定のプロジェクトディレクトリ内でのみ3.12.1を使用するよう設定します：

```bash
# プロジェクトディレクトリで実行
cd /path/to/your/project
pyenv local 3.12.1

# 確認
python --version  # Python 3.12.1と表示されるはず
jp-to-en --help   # ヘルプが表示されるはず
```

これにより、そのディレクトリ内でのみPython 3.12.1が使用されます（.python-versionファイルが作成されます）。

## 方法3: 現在のPython環境にjp-to-enをインストールする

現在使用しているPython環境に直接jp-to-enをインストールします：

```bash
# 現在のPython環境を確認
python --version

# 現在のPython環境にjp-to-enをインストール
pip install jp-to-en
# または
pip install git+https://github.com/cahlchang/jp-to-en.git

# 確認
jp-to-en --help
```

## 方法4: フルパスでコマンドを実行する

jp-to-enがインストールされているPythonバージョンのbinディレクトリ内のコマンドを直接指定して実行します：

```bash
# jp-to-enコマンドの場所を確認
pyenv which -p jp-to-en  # Python 3.12.1の場合

# フルパスで実行
/フルパス/to/jp-to-en terraform_aws_migrator/collectors/aws_ecr.py
```

## 方法5: 仮想環境を使用する

プロジェクト専用の仮想環境を作成してその中にjp-to-enをインストールします：

```bash
# Python 3.12.1を使って仮想環境を作成
pyenv shell 3.12.1
python -m venv myenv

# 仮想環境をアクティブ化
source myenv/bin/activate  # Linuxの場合
# または
source myenv/Scripts/activate  # Windowsの場合

# 仮想環境内にjp-to-enをインストール
pip install jp-to-en

# 確認
jp-to-en --help
```

## pyenvシェル設定の確認

pyenvが正しく設定されていることを確認してください：

```bash
# .bashrcや.zshrcに以下が含まれていることを確認
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"  # virtualenv-pluginを使用している場合
```

シェルの設定を変更した場合は、新しいターミナルを開くか、`source ~/.bashrc`や`source ~/.zshrc`を実行して変更を適用してください。
