from pathlib import Path
import os,re
import markdown as md

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

# ブロック環境の数式の始まりと終わり
block_begin="<div align=\"center\">[tex:\displaystyle{ "
block_end=" }]</div>"
# ブラケットの正規表現
bracket_begin_pat=re.compile('\[')
bracket_end_pat=re.compile('\]')
# パース後のブラケット
parsed_bracket_begin=r'\['
parsed_bracket_end=r'\]'
# 不等号の正規表現
less_than_pat=re.compile('<')
greater_than_pat=re.compile('>')
# パース後の不等号
# \\が2つなのに更にraw文字列としているのは、
# もともと必要な\のエスケープに加え、
# re.sub()のreple引数で使うので、
# reple引数では\を解釈してしまうのでさらにそれをエスケープするため。
parsed_less_than=r'\\lt '
parsed_greater_than=r'\\gt '

def parse_math_block(math_block):
    """
    ブロック環境の数式をパースすする。
    """
    new_math_list=[block_begin]
    for i in range(1,len(math_block)-1):
        line=math_block[i].rstrip(os.linesep)
        # ブラケットをエスケープする
        line=bracket_begin_pat.sub(parsed_bracket_begin, line)
        line=bracket_end_pat.sub(parsed_bracket_end, line)
        # 不等号をMathJax用不等号記号に
        line=less_than_pat.sub(parsed_less_than,line)
        line=greater_than_pat.sub(parsed_greater_than,line)

        new_math_list.append(line)
    new_math_list.append(block_end)
    return "".join(new_math_list)

# インライン環境の数式の正規表現
inline_dollar_pat=re.compile(r'\$(.+?)\$')
# インライン環境の数式の始まりと終わり
inline_begin=r"[tex:\displaystyle{ "
inline_end=" }]"
# インライン版パース後のブラケット
# 最終的に`\\]`と表示されるようにしたいが、
# なぜ\を4つも使った上にraw文字列としているかというと
# https://qiita.com/SolKul/items/8b0f41cf5d8acdcb0b8b
# を参照
inline_parsed_bracket_end=r'\\\\]'
# 指数(キャレット)の正規表現
caret_pat=re.compile('\^')
# エスケープ済み波括弧の正規表現
# `\`が4つなのは
# 1つめは2つ目の`\`をエスケープするため、
# これはPythonが``で文字列を解釈した時点でエスケープが発生
# 3つ目は正規表現でメタ文字に当たる`{`をエスケープするための
# 4つ目の`\`をエスケープするため
# これもPythonが``で文字列を解釈した時点でエスケープが発生
# 4つ目の`\`は正規表現でメタ文字に当たる`{`をエスケープするため
# これは正規表現モジュール`re`がエスケープを解釈する
curly_begin_pat=re.compile('\\\\{')
curly_end_pat=re.compile('\\\\}')
# アンダーバーの正規表現
under_bar_pat=re.compile('_')

def parse_inline_math(math_str):
    conv_math_str=math_str
    # ブラケットをエスケープする
    conv_math_str=bracket_begin_pat.sub(parsed_bracket_begin, conv_math_str)
    conv_math_str=bracket_end_pat.sub(inline_parsed_bracket_end, conv_math_str)
    # 不等号をMathJax用不等号記号に
    conv_math_str=less_than_pat.sub(parsed_less_than,conv_math_str)
    conv_math_str=greater_than_pat.sub(parsed_greater_than,conv_math_str)
    # キャレットの後に空白を
    conv_math_str=caret_pat.sub("^ ",conv_math_str)
    # 波括弧のエスケープをさらにエスケープ
    conv_math_str=curly_begin_pat.sub(r"\\\\{",conv_math_str)
    conv_math_str=curly_end_pat.sub(r"\\\\}",conv_math_str)
    # アンダーバーの前後に空白を
    conv_math_str=under_bar_pat.sub(" _ ",conv_math_str)
    
    return inline_begin+conv_math_str+inline_end    

def parse_plain_block(plain_block):
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
        conv_math_str=parse_inline_math(match_results[i])
        # 一番左にあるインライン数式を変換後の文字列にする。
        # その際、reple引数のエスケープがエスケープされるようにする。
        plain_str=inline_dollar_pat.sub(
            repr(conv_math_str)[1:-1],
            plain_str,
            count=1)
    
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
    for i in range(end_pos):
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

def parse_block_list(md_block_list):
    """
    ブロックのリストそれぞれをパースする
    """
    parsed_list=[]

    for block in md_block_list:
        if block[0] == "plain_block":
            parsed_list.append( parse_plain_block(block[1]) )
        elif block[0] == "math_block":
            parsed_list.append( parse_math_block(block[1]))
    return parsed_list

        
def parse_md_to_hatena(md_path):
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
    parsed_list=parse_block_list(md_block_list)

    # 保存する
    hatena_path=Path(md_path.stem+"_hatena.md")
    hatena_path.write_text("\n".join(parsed_list),encoding='utf-8')