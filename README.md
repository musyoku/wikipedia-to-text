## Wikipedia -> .txt

Wikipediaのダンプデータの記事をそれぞれ1つのテキストファイルに出力します。

## 準備

[/jawiki/latest/](https://dumps.wikimedia.org/jawiki/latest/)から**jawiki-latest-pages-articles.xml.bz2**をダウンロードします。

## ️実行

以下のコマンドで出力ディレクトリにテキストファイルが生成されます。

```bash
python3 run.py -i jawiki-latest-pages-articles.xml.bz2  -o results
```

## 参考
- [Wikipedia Extractor](http://medialab.di.unipi.it/wiki/Wikipedia_Extractor)
