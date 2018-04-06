import re, os
import argparse
import fileinput
import urllib
import codecs

import regex
import collection
import functions


def generate_filename(id, title, namespace):
    filename = title
    filename = filename.replace("/", "_")
    filename = filename.replace(".", "_")
    return os.path.join(args.output_directory, filename + ".txt")


def main():
    try:
        os.mkdir(args.output_directory)
    except:
        pass

    file = fileinput.FileInput(args.input, openhook=fileinput.hook_compressed)
    for (id, title, namespace,
         raw_line_array) in functions.extract_pages_from_archive(file):
        if namespace == "0":
            raw_text = "".join(raw_line_array)
            raw_text = functions.clean(raw_text)
            paragraph_array = []
            for line in functions.compact(raw_text):
                paragraph_array.append(line)
            paragraphs_str = "".join(paragraph_array)
            # 日本語の文章かどうかをチェック
            if paragraphs_str.find("。") == -1:
                continue
            # 指定行数未満のものはスキップ
            sentence_array = paragraphs_str.split("。")
            if (len(sentence_array) < args.minimum_num_lines):
                continue
            # ファイル生成
            print(title, len(sentence_array))
            with codecs.open(
                    generate_filename(id, title, namespace), "w",
                    "utf-8") as f:
                f.write("。\n".join(sentence_array))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="jawiki-latest-pages-articles.xml.bz2のパスを指定")
    parser.add_argument(
        "-o", "--output-directory", type=str, required=True, help="出力ディレクトリ")
    parser.add_argument(
        "-n",
        "--minimum-num-lines",
        type=str,
        default=80,
        help="これ未満の行数の記事はファイルにしない")
    args = parser.parse_args()
    main()