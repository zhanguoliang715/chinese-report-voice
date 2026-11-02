#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""报告体文风门禁。

用法:
    python check_voice.py 正文.txt [更多文件...]
    python check_voice.py 报告.docx        # 需要 python-docx
    python check_voice.py 报告.pdf         # 需要 pymupdf
    python check_voice.py 脚本.py          # 只抽字符串字面量，跳过代码与注释

退出码:
    0  全部通过
    1  有硬性违规（必须改）
    2  只有提示项（可判断后放行）

设计原则：只报不改。改哪一句必须人判断，脚本只负责把问题摊在眼前。
"""

import ast
import re
import sys
from pathlib import Path

# Windows 下重定向到文件时 stdout 默认走 locale（GBK），中文会变乱码。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- 规则表
# 每项: (键, 标题, 正则, 是否硬性)
# 白名单用负向前瞻挡掉中文里的合法构词，避免误报。

RULES = [
    ("dash", "破折号",
     r"——",
     True),
    ("dash2", "单破折号（—）",
     r"(?<!—)—(?!—)",
     True),
    ("narrative", "叙事标记（报告体禁用第一人称情节）",
     r"那天|后来|我们自己|我一开始|记得那|有一次|前几天|当时我们|说实话|说来|没想到",
     True),
    # 「半天」不列入：报告体里「整体耗时达到半天级别」是正式量化表述，
    # 误报过一次。口语形态只有「老半天」「大半天」。
    ("colloq", "口语词",
     r"说白了|其实(?![际施现])|咱们|很慌|差不多|一下就|挺(?![进拔坚])"
     r"|反正|搞不定|弄出来|瞎|难受|爽|坑爹|一堆|老半天|大半天"
     r"|不咋|咋|挺好|挺好的|真是|可不|一堆堆",
     True),
    ("weak", "自我削弱句（与「展现价值」直接相悖）",
     r"仅供参考|仅作参考|不代表大|样本过少|样本有限|由于篇幅|限于能力"
     r"|难免有疏漏|可能存在偏差|本文档不|本报告不|不构成任何|仅供内部",
     True),
    ("hedge", "弱化语气（建议删主语直接陈述）",
     r"我们认为|笔者以为|可以说|不妨说|某种意义",
     False),
]


def read_any(path: Path) -> str:
    """按扩展名取正文。python 文件只取字符串常量，跳过代码与注释。"""
    suf = path.suffix.lower()

    if suf == ".py":
        src = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return src  # 解析不了就整篇扫，另附提示
        out = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                out.append(node.value)
        return "\n".join(out)

    if suf == ".docx":
        try:
            import docx
        except ImportError:
            sys.exit("缺少 python-docx，无法读 .docx")
        d = docx.Document(str(path))
        out = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    out.append(cell.text)
        return "\n".join(out)

    if suf == ".pdf":
        try:
            import pymupdf
        except ImportError:
            sys.exit("缺少 pymupdf，无法读 .pdf")
        d = pymupdf.open(str(path))
        return "\n".join(p.get_text() for p in d)

    return path.read_text(encoding="utf-8", errors="ignore")


def ctx(text: str, m: re.Match, span: int = 14) -> str:
    a = max(0, m.start() - span)
    b = min(len(text), m.end() + span)
    s = text[a:b].replace("\n", " ")
    return ("…" if a else "") + s + ("…" if b < len(text) else "")


def count_numbering(text: str):
    """统计两种编号形态各出现多少次，判断是否混用。"""
    full = len(re.findall(r"^\s*\d+．", text, re.M))     # 1．
    half = len(re.findall(r"^\s*\d+\.\s", text, re.M))   # 1. 
    return full, half


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    hard_fail = 0
    soft_warn = 0

    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            print("文件不存在: %s" % arg)
            hard_fail += 1
            continue

        text = read_any(path)
        zh = len(re.findall(r"[\u4e00-\u9fff]", text))
        print("=" * 68)
        print("%s   中文 %d 字" % (path.name, zh))
        print("=" * 68)

        for key, title, pat, is_hard in RULES:
            hits = list(re.finditer(pat, text))
            if not hits:
                print("  [ok]   %s：0 处" % title)
                continue
            tag = "[FAIL]" if is_hard else "[warn]"
            print("  %s %s：%d 处" % (tag, title, len(hits)))
            for m in hits[:6]:
                print("           · %s" % ctx(text, m))
            if len(hits) > 6:
                print("           · 另有 %d 处未列出" % (len(hits) - 6))
            if is_hard:
                hard_fail += 1
            else:
                soft_warn += 1

        # 编号格式一致性
        full, half = count_numbering(text)
        if full and half:
            print("  [FAIL] 编号格式混用：全角「1．」%d 处，半角「1.」%d 处，只能留一种" % (full, half))
            hard_fail += 1
        elif full or half:
            print("  [ok]   编号格式统一：%s %d 处" % ("全角「1．」" if full else "半角「1.」", full or half))

        # 结构提示：章首导语与章末小结，只提示不改判
        lead = len(re.findall(r"本[章份]|上一章|前述|前文|上述", text))
        summ = len(re.findall(r"第[一二三四五六七八九十\d]+章小结", text))
        print("  [info] 承接词 %d 处，章末小结 %d 处（每章应有 1 处）" % (lead, summ))
        print()

    print("=" * 68)
    if hard_fail:
        print("结论：不通过。%d 项硬性违规，改完重跑。" % hard_fail)
        return 1
    if soft_warn:
        print("结论：可交付，但有 %d 项提示，逐条判断后决定是否改。" % soft_warn)
        return 2
    print("结论：通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
