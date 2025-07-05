import argparse
import sys

from uithub_expander.parser import UithubExpander


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="GitHubリポジトリ構造展開ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python github_extractor.py uithub.txt
  python github_extractor.py uithub.txt -o my_project
  python github_extractor.py uithub.txt --output-dir ./extracted
        """,
    )
    _ = parser.add_argument(
        "input_file",
        help="uithub.com から取得したテキストファイルのパス",
        type=str,
    )
    _ = parser.add_argument(
        "-o",
        "--output-dir",
        default="extracted_repo",
        help="展開先ディレクトリ (デフォルト: extracted_repo)",
        type=str,
    )
    args = parser.parse_args()

    # 抽出処理を実行
    try:
        extractor = UithubExpander(args.input_file, args.output_dir)  # pyright:ignore[reportAny]
        extractor.extract()
    except (FileNotFoundError, UnicodeDecodeError, ValueError, OSError) as e:
        print(f"Error: {e}")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
