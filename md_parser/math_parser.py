from pathlib import Path
import os,re

def parse_math_block(math_block,style="default"):
    if style == "default":
        converted_mb=parse_default_mb(math_block)
    elif style == "katex":
        converted_mb=parse_katex_md(math_block)
    else:
        raise ValueError("invalid style string")
    return converted_mb

def parse_default_mb(math_block):
    """
    ブロック環境の数式をデフォルトのスタイルでパースする。
    """
    # ブロック環境の数式の始まりと終わり
    block_begin="<div align=\"center\">[tex:\displaystyle{ "
    block_end=" }]</div>"
    # ブラケットの正規表現
    bracket_begin_pat=re.compile('\\[')
    bracket_end_pat=re.compile('\\]')
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

def parse_katex_md(math_block):
    """
    ブロック環境の数式を七誌KaTexスタイルでパースする。
    """
    # ブロック環境の数式の始まりと終わり
    block_begin="<div class=\"math-render\">"
    block_end="</div>"
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

    new_math_list=[block_begin]
    for i in range(1,len(math_block)-1):
        line=math_block[i].rstrip(os.linesep)

        # 不等号をHTML用不等号記号に
        line=less_than_pat.sub(parsed_less_than,line)
        line=greater_than_pat.sub(parsed_greater_than,line)

        new_math_list.append(line)
    new_math_list.append(block_end)
    return "".join(new_math_list)


def parse_inline_math(math_str,style="default"):
    if style == "default":
        converted_inline=parse_default_inline(math_str)
    elif style == "katex":
        converted_inline=parse_katex_inline(math_str)
    else:
        raise ValueError("invalid style string")
    return converted_inline

def parse_default_inline(math_str):
    # ブラケットの正規表現
    bracket_begin_pat=re.compile('\\[')
    bracket_end_pat=re.compile('\\]')
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

    conv_math_str=math_str
    # ブラケットをエスケープする
    conv_math_str=bracket_begin_pat.sub(parsed_bracket_begin, conv_math_str)
    conv_math_str=bracket_end_pat.sub(inline_parsed_bracket_end, conv_math_str)
    # 不等号をHTML用不等号記号に
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

def parse_katex_inline(math_str):
    # インライン環境の数式の始まりと終わり
    inline_begin="inline_begin"
    inline_end="inline_end"

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
    # 指数(キャレット)の正規表現
    caret_pat=re.compile('\^')
    # アンダーバーの正規表現
    under_bar_pat=re.compile('_')
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
    # ノルム(エスケープ済みパイプ)の正規表現
    norm_pat=re.compile("\\\\\|")

    conv_math_str=math_str
    # 不等号をHTML用不等号記号に
    conv_math_str=less_than_pat.sub(parsed_less_than,conv_math_str)
    conv_math_str=greater_than_pat.sub(parsed_greater_than,conv_math_str)
    # キャレットの前後に空白を
    conv_math_str=caret_pat.sub(" ^ ",conv_math_str)
    # アンダーバーの前後に空白を
    conv_math_str=under_bar_pat.sub(" _ ",conv_math_str)
    # 波括弧のエスケープをさらにエスケープ
    conv_math_str=curly_begin_pat.sub(r"\\\\{",conv_math_str)
    conv_math_str=curly_end_pat.sub(r"\\\\}",conv_math_str)
    # エスケープ済みパイプをさらにエスケープ
    conv_math_str=norm_pat.sub("\\\\\\\\|",conv_math_str)
    
    return inline_begin+conv_math_str+inline_end 
