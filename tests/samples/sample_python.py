#!/usr/bin/env python3
# coding: utf-8

"""
このモジュールはサンプルの日本語コメントを含むPythonファイルです。
jp-to-enツールのテストに使用します。

様々な種類のコメントが含まれています：
- 単一行コメント
- 複数行コメント
- インラインコメント
"""

import os
import sys
from typing import List, Dict, Optional


# ユーティリティ関数の定義
def calculate_sum(numbers: List[int]) -> int:
    """
    整数リストの合計を計算する関数
    
    Args:
        numbers: 合計を計算する整数のリスト
        
    Returns:
        整数の合計値
    """
    total = 0
    for num in numbers:
        total += num  # 合計に加算
    return total


class DataProcessor:
    """
    データ処理を行うサンプルクラス
    このクラスはデータの読み込み、処理、保存を担当します。
    """
    
    def __init__(self, input_path: str, output_path: Optional[str] = None):
        """
        DataProcessorを初期化する
        
        Args:
            input_path: 入力ファイルのパス
            output_path: 出力ファイルのパス（省略可能）
        """
        self.input_path = input_path
        self.output_path = output_path or input_path + ".processed"
        self.data = []  # データを格納するリスト
    
    def load_data(self) -> bool:
        """
        入力ファイルからデータを読み込む
        
        Returns:
            成功した場合はTrue、失敗した場合はFalse
        """
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.data = f.readlines()  # 全行を読み込む
            return True
        except Exception as e:
            # エラーが発生した場合はログに記録
            print(f"読み込みエラー: {e}", file=sys.stderr)
            return False
    
    def process_data(self) -> None:
        """データを処理する"""
        if not self.data:
            return  # データが空の場合は何もしない
            
        # データの前処理
        self.data = [line.strip() for line in self.data]
        
        # 空行を削除
        self.data = [line for line in self.data if line]
        
        # 重複を削除
        self.data = list(set(self.data))
        
        # データをソート
        self.data.sort()
    
    def save_data(self) -> bool:
        """
        処理したデータを出力ファイルに保存する
        
        Returns:
            成功した場合はTrue、失敗した場合はFalse
        """
        try:
            # 出力ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
            
            with open(self.output_path, 'w', encoding='utf-8') as f:
                for line in self.data:
                    f.write(line + '\n')  # 各行を書き込む
            return True
        except Exception as e:
            # 保存中にエラーが発生した場合
            print(f"保存エラー: {e}", file=sys.stderr)
            return False
    
    def run(self) -> bool:
        """
        全処理を実行する
        
        データの読み込み、処理、保存を順番に実行します。
        いずれかのステップが失敗した場合は処理を中止します。
        
        Returns:
            すべての処理が成功した場合はTrue、それ以外はFalse
        """
        # 処理ステップを実行
        if not self.load_data():
            return False  # データ読み込みに失敗
            
        self.process_data()  # データを処理
        
        if not self.save_data():
            return False  # データ保存に失敗
            
        return True  # すべての処理が成功


# このスクリプトが直接実行された場合の処理
if __name__ == "__main__":
    # コマンドライン引数の検証
    if len(sys.argv) < 2:
        print("使用方法: python sample_python.py 入力ファイル [出力ファイル]", file=sys.stderr)
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # プロセッサーの作成と実行
    processor = DataProcessor(input_file, output_file)
    success = processor.run()
    
    # 処理結果を表示
    if success:
        print("処理が完了しました！")  # 処理成功
    else:
        print("処理中にエラーが発生しました。", file=sys.stderr)  # 処理失敗
        sys.exit(1)
