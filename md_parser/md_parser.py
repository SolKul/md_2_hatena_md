from pathlib import Path
import os,re

from . import math_parser

def classfy_math_block(md_list,pos,end_pos):
    """
    ブロック環境の数式を検知する。
    """
    # $$があるかどうか。
    if ('$$' in md_list[pos]):
        math_block_start_pos=pos
        # 終わりの$$が出てくるまで読み込む
        for i in range(pos+1,end_pos):
            if '$$' in md_list[i]:
                math_block_end_pos=i
                break
        math_block=md_list[math_block_start_pos:math_block_end_pos+1].copy()
        # ブロックの種類とブロックのリストをタプルにする
        block_tuple=("math_block",math_block)
        # タプルとブロックの終わりの位置を返す
        return block_tuple,math_block_end_pos
    else:
        # $$が無い場合
        return None,pos

# インライン環境の数式の正規表現
inline_dollar_pat=re.compile(r'\$(.+?)\$')

def parse_plain_block(plain_block,style="default"):
    """
    インライン数式を`findall`ですべて検索し、順次変換する。
    """
    # 標準ブロックをすべて結合し、文字列にする
    plain_str="".join(plain_block)
    # インライン数式をすべて探し、
    #「inline_math_数字」と置換する。
    match_results=inline_dollar_pat.findall(plain_str)
    match_num=len(match_results)
    parsing_math_list=[]
    for i in range(match_num):
        # インライン数式を変換する。
        conv_math_str=math_parser.parse_inline_math(
            match_results[i],
            style=style)
        # 一番左にあるインライン数式を変換後の文字列にする。
        # その際、reple引数のエスケープがエスケープされるようにする。
        plain_str=inline_dollar_pat.sub(
            repr(conv_math_str)[1:-1],
            plain_str,
            count=1)

    if style == "katex":
        plain_str=plain_str.replace("inline_begin","[]$")
        plain_str=plain_str.replace("inline_end","$[]")
    
    return plain_str

def classify_blocks(md_whole):
    """
    文章全体を標準ブロック、数式ブロックなどとブロックごとのリストに分ける
    """
    # 今何行目か(position)
    pos=0
    previous_pos=0
    # ブロックのリスト
    md_block_list=[]
    end_pos=len(md_whole)
    for i in range(end_pos+1):
        # 行数が最終行以降であれば、抜ける
        if pos >= end_pos:
            plain_block=md_whole[previous_pos:pos].copy()
            md_block_list.append(
                ("plain_block",
                plain_block)
            )
            break
        block_tuple,block_end_pos=classfy_math_block(md_whole,pos,end_pos)
        # ブロックが検知された場合は
        if block_tuple is not None:
            # 標準ブロックをplain_blockとしてタプルにし追加
            plain_block=md_whole[previous_pos:pos].copy()
            md_block_list.append(
                ("plain_block",
                plain_block)
            )
            # 今回検知されたブロックを追加
            md_block_list.append(block_tuple)
            # 行数をブロックの最終行に
            pos=block_end_pos
            previous_pos=block_end_pos+1
        pos+=1
    return md_block_list

def parse_block_list(md_block_list,style="default"):
    """
    ブロックのリストそれぞれをパースする
    """
    parsed_list=[]

    for block in md_block_list:
        if block[0] == "plain_block":
            parsed_list.append( parse_plain_block(
                block[1],
                style=style))
        elif block[0] == "math_block":
            parsed_list.append( math_parser.parse_math_block(
                block[1],
                style=style))
    if style == "katex":
        n7shi_script="""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.css" integrity="sha384-bsHo4/LA+lkZv61JspMDQB9QP1TtO4IgOf2yYS+J6VdAYLVyx1c3XKcsHh0Vy8Ws" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.js" integrity="sha384-4z8mjH4yIpuK9dIQGR1JwbrfYsStrNK6MP+2Enhue4eyo0XlBDXOIPc8b6ZU0ajz" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/contrib/auto-render.min.js" integrity="sha384-kWPLUVMOks5AQFrykwIup5lo0m3iMkkHrD0uJ4H5cjeGihAutqP0yW0J6dpFiVkI" crossorigin="anonymous"></script>
<script>
document.addEventListener("DOMContentLoaded", () => {
  for (let e of Array.from(document.getElementsByClassName("math-render"))) {
    if (!e.mathRendered) {
      try {
        katex.render(e.textContent, e, { displayMode: true });
      } catch (ex) {
        e.textContent = ex.message;
      }
      e.mathRendered = true;
    }
  }
  let katexOptions = { delimiters: [{ left: "$", right: "$", display: false }] };
  for (let e of Array.from(document.getElementsByClassName("entry-content"))) {
    renderMathInElement(e, katexOptions);
  }
});
</script>"""
        parsed_list.append(n7shi_script)
    return parsed_list

        
def parse_md_to_hatena(md_path,style="default"):
    """
    pathlibのPathを受け取って、
    markdownをはてな流mdにパースして、
    もとのファイル名_hatena.mdとして保存する
    """
    with md_path.open(encoding='utf-8',mode='r') as f:
        md_whole=f.readlines()

    if md_whole is None:
        return None
    md_block_list=classify_blocks(md_whole)
    parsed_list=parse_block_list(md_block_list,style=style)

    # 保存する
    hatena_path=Path(md_path.stem+"_hatena.md")
    hatena_path.write_text("\n".join(parsed_list),encoding='utf-8')