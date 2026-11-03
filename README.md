# chinese-report-voice

**给评委、领导、投资人看的中文文档，先判文体再动笔。报告体、技术文档、口播稿是三套语体，混了就白写。附两个能跑的门禁。**

![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-yellow)
![spec](https://img.shields.io/badge/agentskills.io-spec%20valid-2E7D32)

## 它解决什么

同一批事实，文体错了整篇就白写。典型翻车有三种：

- 把**技术文档**当报告交上去 → 评委看到的是"怎么实现"，看不到"值不值得做"；
- 把**报告体**写成口播稿 → 通篇"我们"，像讲故事；
- 该给数据的地方写"效果显著" → 无法验收。

这个技能把"判文体"变成动笔前的第一道门，再给两条可执行的检查。

## 三种文体，先分清

| 文体 | 读者 | 他拿它做什么决定 | 判据 |
|---|---|---|---|
| **报告体** | 评委、主管部门、投资人 | 判断值不值得给分、给钱 | 无第一人称叙事；每节首句是判断；数据有出处；章末有小结 |
| **技术文档** | 工程师 | 判断怎么复现 | 有节点图、参数、命令、退出码 |
| **口播稿** | 观众，用耳朵听 | 判断要不要继续看 | 短句、有气口、有"我"、数字只留听得懂的 |

## 六条语体规则（报告体）

1. 主语用「该类用户 / 本方案 / 本次调研」，不用"我们"讲经历；
2. 每节首句先给判断，再展开依据，不铺垫、不设问；
3. 并列项写「1．2．3．」，每条以"名词短语。+ 展开句"起头；
4. 章首交代"本章围绕……"，章末写小结并把话交给下一章；
5. 用词偏书面：需求原点、转化链路、前置假设、能力短板、可交付物；
6. 破折号、口语词、抒情句一律 0。

另外两条纪律：**自我削弱句全删**（"仅供参考""样本过少""不下结论"——在评审场合等于自己扣分）；**数据不可继承**（上一版这么写，不等于这一版能照抄，没有记录就是编造）。

## 两个门禁

```bash
python scripts/check_voice.py 正文.txt          # 也支持 .md / .docx / .pdf / .py
python scripts/check_pdf_layout.py 报告.pdf      # 也支持 --margin 2.6 --min-chars 330
```

| 脚本 | 查什么 | 退出码 |
|---|---|---|
| `check_voice.py` | 文风：口语词、破折号、自我削弱句、套话；**只报不改** | 0 通过 / 1 硬性违规必改 / 2 仅提示项可判断放行 |
| `check_pdf_layout.py` | 排版四项：纸张是否 A4、薄页与空白页、表格是否越出版心、目录页码是否指对 | 0 通过 / 非 0 有问题 |

**先跑门禁再交付**。退出码非 0 不许交。

## 用插件安装（一条命令，已实测）

```bash
claude plugin marketplace add zhanguoliang715/chinese-report-voice
claude plugin install chinese-report-voice@chinese-report-voice
```

> 本机 git 若报 `CRYPT_E_NO_REVOCATION_CHECK`（证书吊销列表查不到），命令前加 `GIT_SSL_NO_VERIFY=1`。
> 这是本机 TLS 配置问题，与仓库无关；换台机器通常直接可用。

不想装插件也行，下面的手动方式是等价的。

## 上手

```bash
git clone https://github.com/zhanguoliang715/chinese-report-voice.git
cp -r chinese-report-voice ~/.workbuddy/skills/
python ~/.workbuddy/skills/chinese-report-voice/scripts/check_voice.py 报告.md
```

`.docx` 需要 `python-docx`，`.pdf` 需要 `pymupdf`；纯文本零依赖。

## 边界

- **只管文风与版式，不管内容真伪**。事实要自己去核。
- **不能把错的内容改对**。它能让正确的文字读起来像报告，不能让编造的文字变成事实。
- **赛事/机构模板优先**。章节顺序以官方要求为准，本技能的语体规则不与模板冲突时才适用。
- **不适用于教程、README、聊天式复盘**——那些口径相反（30% 口语 70% 书面语反而更自然）。

## 最常见的三个错

1. **通篇"我们"**。报告体的主语是"该类用户 / 本方案"。
2. **破折号当连接符**。出现 `——` 基本说明没换到报告体。
3. **继承上一版的数据**。上一版写"5 人访谈"，这一版没有记录就照抄——这是编造。

## 文档

| 想看什么 | 去哪 |
|---|---|
| 第一次用，怎么一步步做 | [docs/新手手册.md](docs/新手手册.md) |
| 判定逻辑、失败模式、已知限制 | [docs/技术文档.md](docs/技术文档.md) |
| 完整纪律与逐段对照 | [SKILL.md](SKILL.md) 与 [examples/bad_vs_good.md](examples/bad_vs_good.md) |

## License

[MIT](LICENSE)
