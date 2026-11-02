#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Word/PDF 交付前排版体检。

用法:
    python check_pdf_layout.py 报告.pdf
    python check_pdf_layout.py 报告.pdf --margin 2.6 --min-chars 330

检查四项:
    1. 纸张是否为 A4（595×842 pt）——Letter 是 612×792，一眼可辨
    2. 薄页与空白页——正文字数低于阈值的页全部列出
    3. 表格是否越出版心——表格外框超出「页宽 − 边距」的列出
    4. 目录页码是否指对——逐条比对目录声明的页与章节标题实际所在页

退出码:
    0  全部通过
    1  有硬性问题（空白页、表格越界、目录页码错）

依赖: pymupdf
"""

import re
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    sys.exit("缺少 pymupdf，先装：pip install pymupdf")

# Windows 下重定向到文件时 stdout 默认走 locale（GBK），中文会变乱码，
# 后续用 grep 查日志就查不到。统一改 UTF-8。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


A4 = (595.28, 841.89)
LETTER = (612.0, 792.0)
CM = 28.3465          # 1cm = 28.3465pt
HEADER_ZONE = 55      # 页眉区 y 上限，低于此的块不算正文
FOOTER_GAP = 30       # 页脚区高度


def parse_args(argv):
    if len(argv) < 2:
        print(__doc__)
        sys.exit(2)
    pdf = Path(argv[1])
    margin, min_chars = 2.6, 330
    for i, a in enumerate(argv):
        if a == "--margin" and i + 1 < len(argv):
            margin = float(argv[i + 1])
        if a == "--min-chars" and i + 1 < len(argv):
            min_chars = int(argv[i + 1])
    return pdf, margin, min_chars


def body_blocks(page, bottom):
    """只取正文区的文字块，避开页眉页脚。"""
    return [b for b in page.get_text("blocks")
            if HEADER_ZONE < b[1] and b[3] < bottom + 6]


def check_paper(doc):
    w, h = doc[0].rect.width, doc[0].rect.height
    ok = abs(w - A4[0]) < 3 and abs(h - A4[1]) < 3
    kind = "A4" if ok else ("Letter" if abs(w - LETTER[0]) < 3 and abs(h - LETTER[1]) < 3 else "自定义")
    print("  纸张：%.0f×%.0f pt → %s %s" % (w, h, kind, "[ok]" if ok else "[FAIL] 应为 A4 595×842"))
    return ok


CHAPTER_RE = re.compile(r"^\s*([一二三四五六七八九十]+、|第[一二三四五六七八九十]+章|附录\s*[A-ZＡ-Ｚ])")


def is_chapter_head(page):
    """下一页开头是不是一级章标题。用于区分「章末余页」与「真孤页」。"""
    lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
    for l in lines[1:4]:          # 跳过页眉
        if CHAPTER_RE.match(l):
            return True
    return False


def check_thin(doc, min_chars):
    """两档判定：
         空白页 / 极薄页（< min_chars*0.6）        → 硬性问题
         偏薄页但下一页是新章标题（章末余页）      → 正常，只记一行
         偏薄页且下一页仍是同章正文（真孤页）      → 硬性问题
       这条区分是本脚本的关键：一章结束时剩下的空白是排版正常结果，
       整章正文被挤到下一页只剩两行才是坏页。
    """
    fatal, benign = [], []
    for i, pg in enumerate(doc):
        n = len(pg.get_text().strip())
        if n >= min_chars:
            continue
        nxt_is_head = (i == len(doc) - 1) or is_chapter_head(doc[i + 1])
        head = pg.get_text().strip().replace("\n", " ")[:44]
        if n < 60 or not nxt_is_head:
            fatal.append((i + 1, n, "空白页" if n < 60 else "孤页", head))
        else:
            benign.append((i + 1, n, head))

    if not fatal and not benign:
        print("  薄页：无（阈值 %d 字）[ok]" % min_chars)
        return True
    if benign:
        print("  章末余页 %d 处（下一页是新章，属正常）[ok]" % len(benign))
        for pg, n, head in benign:
            print("         p%02d  %4d 字  %s" % (pg, n, head))
    if fatal:
        print("  孤页 / 空白页 %d 处 [FAIL]——需要按整行压缩上一页" % len(fatal))
        for pg, n, kind, head in fatal:
            print("         p%02d  %4d 字  %s  %s" % (pg, n, kind, head))
        return False
    return True


def check_tables(doc, margin):
    W = doc[0].rect.width
    left, right = margin * CM, W - margin * CM
    print("  版心：%.1f ~ %.1f pt（边距 %.1fcm）" % (left, right, margin))
    bad = []
    for i, pg in enumerate(doc):
        for dr in pg.get_drawings():
            r = dr["rect"]
            if r.width > 60 and r.height > 10 and (r.x0 < left - 1 or r.x1 > right + 1):
                bad.append((i + 1, round(r.x0, 1), round(r.x1, 1)))
    if not bad:
        print("  表格：全部在版心内 [ok]")
        return True
    print("  表格越界：%d 处 [FAIL]" % len(bad))
    for pg, x0, x1 in bad[:10]:
        print("         p%02d  x0=%.1f  x1=%.1f" % (pg, x0, x1))
    return False


def check_toc(doc):
    """目录条目形如「第一章 痛点调研 ……… 4」。找不到目录页就跳过。"""
    claims = []
    toc_page = None
    for i, pg in enumerate(doc[:6]):
        found = re.findall(r"([^\n.]{4,40}?)\s*[.·]{3,}\s*(\d+)\s*$", pg.get_text(), re.M)
        if len(found) >= 4:
            claims, toc_page = found, i + 1
            break

    if not claims:
        print("  目录：未识别到带点线的目录页，跳过 [info]")
        return True

    print("  目录：p%d 共 %d 条，逐条核对" % (toc_page, len(claims)))
    bad = 0
    for name, pgno in claims:
        name = name.strip()
        pgno = int(pgno)
        if pgno < 1 or pgno > len(doc):
            print("         [FAIL] %-24s 声明 p%d 超出总页数" % (name, pgno))
            bad += 1
            continue
        lines = [l.strip() for l in doc[pgno - 1].get_text().splitlines() if l.strip()]
        key = name.replace(" ", "")[:8]
        hit = any(l.replace(" ", "").startswith(key) for l in lines[1:5])
        if hit:
            print("         [ok]   %-24s p%d" % (name, pgno))
        else:
            print("         [FAIL] %-24s 声明 p%d，该页开头是：%s"
                  % (name, pgno, " | ".join(lines[1:3])))
            bad += 1
    return bad == 0


def main():
    pdf, margin, min_chars = parse_args(sys.argv)
    if not pdf.exists():
        sys.exit("文件不存在: %s" % pdf)

    doc = pymupdf.open(str(pdf))
    print("=" * 68)
    print("%s   共 %d 页" % (pdf.name, len(doc)))
    print("=" * 68)

    r1 = check_paper(doc)
    r2 = check_thin(doc, min_chars)
    r3 = check_tables(doc, margin)
    r4 = check_toc(doc)

    print("=" * 68)
    if r1 and r2 and r3 and r4:
        print("结论：排版通过。")
        return 0
    print("结论：不通过。逐条处理完重跑。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
