"""GitHub リポジトリ構造展開ツール
uithub.com から取得したテキストファイルを実際のディレクトリ構造に展開します。

このモジュールは、uithub.comで生成されるリポジトリ構造のテキスト表現を
実際のファイルシステム上のディレクトリとファイルに変換する機能を提供します。

Example:
    ```python
    expander = UithubExpander("uithub.txt", "output_dir")
    expander.extract()
    ```

Notes:
    - 入力ファイルはUTF-8エンコーディングである必要があります
    - 出力ディレクトリは事前に存在している必要があります
    - ファイル内容は行番号付きの形式から自動的にクリーンアップされます
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class UithubExpander:
    """uithub.com から取得したテキストファイルを実際のディレクトリ構造に展開するクラス

    このクラスは、uithub.comで生成されるリポジトリ構造のテキスト表現を解析し、
    実際のファイルシステム上のディレクトリとファイルに変換します。

    Attributes:
        input_file (Path): 入力ファイルのパス
        output_dir (Path): 出力ディレクトリのパス
        files_content (dict[str, str]): ファイルパスと内容のマッピング
        tree_structure (list[str]): ツリー構造の行のリスト

    Raises:
        FileNotFoundError: 入力ファイルまたは出力ディレクトリが存在しない場合
        OSError: ファイル作成に失敗した場合
        UnicodeDecodeError: ファイルのエンコーディングがUTF-8でない場合
        ValueError: ファイル内容のパターンが見つからない場合
        Exception: その他の処理中に発生したエラー

    Notes:
        - ファイル内容は行番号付きの形式から自動的にクリーンアップされます
        - ツリー構造はASCII文字 (├──、└──、│) を使用した形式を解析します
        - ディレクトリ構造は自動的に作成され、既存のファイルは上書きされます
    """

    def __init__(self, input_file: str, output_dir: str = "extracted_repo") -> None:
        """UithubExpanderクラスの初期化

        Args:
            input_file: uithub.txtファイルのパス。ファイルが存在しない場合はFileNotFoundErrorを発生
            output_dir: 展開先ディレクトリ。ディレクトリが存在しない場合はFileNotFoundErrorを発生

        Raises:
            FileNotFoundError: 入力ファイルまたは出力ディレクトリが存在しない場合

        Notes:
            - 入力ファイルと出力ディレクトリの存在チェックを行います
            - パスはPathlibオブジェクトに変換されて内部で管理されます
            - デフォルトの出力ディレクトリは"extracted_repo"です
        """
        _input_file = Path(input_file)
        if not _input_file.exists():
            msg = f"Not found input file: '{input_file}'"
            raise FileNotFoundError(msg)

        _output_dir = Path(output_dir)
        if not _output_dir.exists():
            msg = f"Output directory not found. '{output_dir}' will be created."
            logger.warning(msg)
        else:
            msg = f"Overwrite the output directory: '{output_dir}'"
            logger.warning(msg)

        self.input_file: Path = _input_file
        self.output_dir: Path = _output_dir
        self.files_content: dict[str, str] = {}
        self.tree_structure: list[str] = []

    def parse_file(self) -> None:
        """入力ファイルを解析してツリー構造とファイル内容を分離

        入力ファイルを読み込み、ファイル内容とツリー構造を抽出します。
        このメソッドは他のメソッドを呼び出して実際の解析処理を行います。

        Raises:
            UnicodeDecodeError: ファイルのエンコーディングがUTF-8でない場合

        Notes:
            - ファイルはUTF-8エンコーディングで読み込まれます
            - 解析結果はインスタンス変数 (files_content, tree_structure) に保存されます
            - このメソッドはextract()メソッドから自動的に呼び出されます
        """
        try:
            with self.input_file.open(encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                e.reason,
            ) from e

        # ファイル内容を分離
        self._extract_file_contents(content)

        # ツリー構造を抽出
        self._extract_tree_structure(content)

    def _extract_file_contents(self, content: str) -> None:
        """ファイル内容を抽出

        入力ファイルの内容から、ファイルパスとその内容を抽出します。
        行番号付きの形式からクリーンアップされた内容を取得します。

        Args:
            content: 入力ファイルの全内容

        Raises:
            ValueError: ファイル内容のパターンが見つからない場合

        Notes:
            - ファイル内容のパターン: "/path/to/file:" に続く区切り線 (40文字以上の-) と内容
            - 行番号パターン (例: " 1 | ") は自動的に除去されます
            - 抽出された内容はself.files_contentに保存されます
            - ファイルパスから先頭のスラッシュは除去されます
        """
        # ファイル内容のパターン: /path/to/file: に続く区切り線と内容
        # pattern = r'^(/[^:]+):\s*\n-{40,}\s*\n(.*?)(?=\n\n(?:/[^:]+:|\Z))'
        pattern = r"^(?P<path>/[^:]+):\s*\n-{40,}\s*\n(?P<content>[\w\W]*?)(?P<tail>\n\n)"
        matches: list[tuple[str, str, str]] = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

        if len(matches) == 0:
            msg = "No matches found in the input file: "
            msg += f"{len(content.splitlines())} lines are loaded"
            raise ValueError(msg)

        for file_path, file_content, _ in matches:
            # 先頭のスラッシュを除去
            clean_path = file_path.lstrip("/")

            # 行番号を除去してファイル内容をクリーンアップ
            lines = file_content.split("\n")
            cleaned_lines: list[str] = []

            for line in lines:
                # 行番号パターン (例: " 1 | ") を除去
                line_match = re.match(r"^\s*\d+\s*\|\s?(\s*.*)", line)
                if line_match:
                    cleaned_lines.append(line_match.group(1))
                elif line.strip():  # 空行でない場合はそのまま追加
                    cleaned_lines.append(line)

            self.files_content[clean_path] = "\n".join(cleaned_lines)

    def _extract_tree_structure(self, content: str) -> None:
        """ツリー構造を抽出

        入力ファイルの内容から、ディレクトリツリー構造を表す行を抽出します。

        Args:
            content: 入力ファイルの全内容

        Notes:
            - ツリー構造は "├──", "└──" で始まる行から開始されます
            - 空行でツリー構造の終了を判定します
            - ツリー構造の行 (├──、└──、│、インデント) のみを抽出します
            - 抽出された行はself.tree_structureに保存されます
        """
        lines = content.split("\n")
        in_tree = False

        for line in lines:
            # ツリー構造の開始を検出
            if line.startswith(("├──", "└──")):
                in_tree = True

            # ツリー構造の終了を検出 (空行で判断)
            if in_tree and line.strip() == "":
                break

            # ツリー構造の行を保存
            if in_tree and line.startswith(("├──", "└──", "│", "    ")):
                self.tree_structure.append(line)

    def create_directory_structure(self) -> None:
        """ディレクトリ構造を作成

        解析されたファイル内容とツリー構造に基づいて、
        実際のファイルシステム上にディレクトリとファイルを作成します。

        Raises:
            OSError: ファイル作成に失敗した場合

        Notes:
            - 出力ディレクトリが存在しない場合は自動的に作成されます
            - ディレクトリはファイルより先に作成されます (パス順ソート)
            - ファイル内容に含まれるパスの親ディレクトリも自動的に作成されます
            - 既存のファイルは上書きされます
            - 作成されたファイルとディレクトリは標準出力に表示されます
            - ファイル作成に失敗した場合はエラーメッセージが表示されますが、処理は継続されます
        """
        # 出力ディレクトリを作成
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 全てのファイルとディレクトリのパスを収集
        all_paths: set[str] = set()

        # ファイル内容に含まれるパスも追加
        for file_path in self.files_content:
            all_paths.add(file_path)
            # 親ディレクトリも追加
            parent_parts = file_path.split("/")[:-1]
            for i in range(len(parent_parts)):
                parent_path = "/".join(parent_parts[: i + 1])
                all_paths.add(parent_path)

        # パスをソートしてディレクトリから先に作成
        sorted_paths = sorted(all_paths)

        for path in sorted_paths:
            full_path = self.output_dir / path

            # セキュリティチェックを行う (トラバーサル攻撃対策)
            try:
                if not full_path.resolve().is_relative_to(self.output_dir.resolve()):
                    msg = f"Skipping path: {full_path}"
                    logger.warning(msg)
                    continue
            except FileNotFoundError:
                pass
            except Exception as e:
                msg = f"Error: {e}"
                logger.exception(msg)
                continue

            # ディレクトリかファイルかを判定
            if path in self.files_content:
                # ファイルの場合
                full_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with full_path.open("w", encoding="utf-8") as f:
                        _ = f.write(self.files_content[path])
                    msg = f"Created file: {full_path}"
                    logger.info(msg)
                except OSError as e:
                    msg = f"Failed to create file: {full_path}: {e}"
                    logger.exception(msg)
            else:
                # ディレクトリの場合 (ファイル内容に含まれていないパス)
                full_path.mkdir(parents=True, exist_ok=True)
                msg = f"Created directory: {full_path}"
                logger.info(msg)

    def extract(self) -> None:
        """メイン処理: ファイルを解析してディレクトリ構造を展開

        このメソッドは、UithubExpanderクラスの主要な処理を実行します。
        ファイルの解析からディレクトリ構造の作成まで、一連の処理を行います。

        Raises:
            FileNotFoundError: 入力ファイルまたは出力ディレクトリが存在しない場合
            UnicodeDecodeError: ファイルのエンコーディングがUTF-8でない場合
            ValueError: ファイル内容のパターンが見つからない場合
            Exception: その他の処理中に発生したエラー

        Notes:
            - 処理の進行状況が標準出力に表示されます
            - エラーが発生した場合は詳細なエラーメッセージが表示されます
            - 処理は段階的に実行され、各段階でエラーハンドリングが行われます
            - 成功時は作成されたファイル数が表示されます
        """
        msg = f"Input file: {self.input_file}"
        logger.info(msg)
        msg = f"Output directory: {self.output_dir}"
        logger.info(msg)
        logger.info("-" * 50)

        try:
            # ファイルを解析
            self.parse_file()

            msg = f"Detected files: {len(self.files_content)}"
            logger.info(msg)
            msg = f"Tree structure lines: {len(self.tree_structure)}"
            logger.info(msg)

            # ディレクトリ構造を作成
            self.create_directory_structure()

            msg = "Expansion completed!"
            logger.info(msg)
            msg = f"Created files: {len(self.files_content)}"
            logger.info(msg)

        except Exception as e:
            msg = f"Error: {e}"
            logger.exception(msg)
            raise
