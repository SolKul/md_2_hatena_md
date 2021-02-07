# Markdownをはてな流Markdownにパースする
Markdown中の数式をてなブログのはてな流の数式に変換するプログラムです。Markdown全体を一括で変換します。

## 使用方法

`md_parser`フォルダ内の`md_parser.py`を次のようにインポートして使います。

```python
from md_parser import md_parser
md_parser.parse_md_to_hatena(pathlib.Pathオブジェクト,style="default")
```

`style`でスタイルを指定できます。

- デフォルトの`default`ははてなブログにそのまま数式を渡す形になります。はてなブログは数式の表示にGoogle Charts APIかMathJaxを使っているらしいです。これはかなり遅いです。
- `katex`を指定すれば、KaTeXで高速にレンダリングしてくれるようになります。[KaTeXのテスト - 七誌の開発日記](https://7shi.hateblo.jp/entry/2018/07/28/231859)のコードをお借りしました。また、数式についてはてなキーワードの自動リンクを無効にするようにしているので、はてなキーワードの自動リンクに気を遣う必要はありません。

レポジトリ内の`main.py`を実行すると`Sample.md`がパースされ、パースされた`Sample_hatena.md`というファイルができるはずです。


## 動機
はてなブログのMarkdownは

- 画面半々にしてプレビューできるがスクロールが同期しない
- 数式がプレビューされない
- 数式の記法がLaTeXの普通の記法と異なる(キャレット、アンダーバーなど)

と使いづらいです。

そこで、VSCodeの拡張機能の一つである`Markdown Preview Enhanced`でMarkdownをプレビューしながら文章や数式を書き、それをはてな流のMarkdownにパースすることにしました。これで数式を含むQiitaの記事をはてなブログに移植するのも楽になると思います。

`Markdown Preview Enhanced`についてはこちら

https://qiita.com/tamaki_osamu/items/b5785930a77d44bba59c


## 数式の記法

`Markdown Preview Enhanced`ではいくつかの数式の挿入方法がサポートされていますが、そのうち`$$`で囲まれたブロック数式、`$`で囲まれたインライン数式に対応しています。しかし、

````MarkDown
```math
e^{i\pi} = -1
```
````

には対応していません。


## 実装

もとの`md`ファイルをリスト化し、文章全体を標準ブロック、数式ブロックなどとブロックごとのリストに分けてます。標準ブロックについては標準ブロック内のインライン数式を`re.findall`ですべて検索し、順次はてな流インライン数式に変換します。数式ブロックにつていもはてなブログ用の数式ブロックになるように変換します。最後に`"".join()`で結合し、保存しています。

数式の変換については、(`style`で`default`を指定した場合)

- ブロック数式(`$$`で囲まれた数式)

1. `<div align="center">[tex:`と`]</div>`で囲む
2. `]`を`\]`に置換
3. `<`、`>`を`\lt`、`\gt`に変換

- インライン数式(`$`で囲まれた数式)

1. `[tex:\displaystyle{`と`}]`で囲む
2. `^`(指数)の後ろにスペースを挿入
3. `_`(添え字)の前後にスペースを挿入
4. `\{`,`\}`,`]`を`\\{`,`\\}`,`\\]`に置換
5. `<`、`>`を`\lt`、`\gt`に変換

## 注意
うまくパースできなくても責任は取れないです。あくまでこういう事ができるという例です。

## 必要環境
python3.8以上。`pathilib`モジュールを使います。

## 参考サイト

以下のサイトを参考にさせていただきました。ありがとうございました。

https://7shi.hateblo.jp/entry/2018/07/27/185311

https://ano3.hatenablog.com/entry/2020/04/15/034609
