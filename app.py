import io
import os
import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, Query, Response
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
app = FastAPI()
# 常用字体自适应候选
FONT_PATHS_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:\\Windows\\Fonts\\msyhbd.ttc",
]
FONT_PATHS_REGULAR = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
]
FONT_PATHS_SERIF_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

def resolve_font(candidates: List[str]) -> str:
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""

FONT_BOLD = resolve_font(FONT_PATHS_BOLD)
FONT_REGULAR = resolve_font(FONT_PATHS_REGULAR)
FONT_SERIF_BOLD = resolve_font(FONT_PATHS_SERIF_BOLD)

def get_font(path: str, size: int):
    if path and os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    return lines

def create_rich_background(width: int, height: int) -> Image.Image:
    base = Image.new("RGBA", (width, height), (11, 17, 32, 255))
    draw = ImageDraw.Draw(base)

    for y in range(height):
        ratio = y / height
        r = int(12 * (1 - ratio) + 8 * ratio)
        g = int(24 * (1 - ratio) + 14 * ratio)
        b = int(45 * (1 - ratio) + 24 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx1, cy1, r1 = width - 150, 200, 450
    for r in range(r1, 0, -10):
        glow_draw.ellipse([cx1 - r, cy1 - r, cx1 + r, cy1 + r], fill=(14, 165, 233, int(45 * (1 - r / r1))))

    cx2, cy2, r2 = 120, 1000, 400
    for r in range(r2, 0, -10):
        glow_draw.ellipse([cx2 - r, cy2 - r, cx2 + r, cy2 + r], fill=(99, 102, 241, int(25 * (1 - r / r2))))

    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for gx in range(40, width, 40):
        for gy in range(40, height, 40):
            grid_draw.rectangle([gx, gy, gx + 2, gy + 2], fill=(255, 255, 255, 14))

    for ly in [140, 380, 720, 1650, 2450]:
        if ly < height:
            grid_draw.line([(0, ly), (width, ly)], fill=(56, 189, 248, 18), width=1)

    final_bg = Image.alpha_composite(base, glow)
    final_bg = Image.alpha_composite(final_bg, grid)
    return final_bg.convert("RGB")

def get_comprehensive_data():
    now = datetime.datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    
    return {
        "date_str": now.strftime("%Y年%m月%d日"),
        "weekday_str": weekdays[now.weekday()],
        "lunar_str": "农历九月初三 · 寒露",
        "history_events": [
            {"year": "1884年", "text": "华盛顿国际子午线会议正式确立格林尼治天文台为世界本初子午线及全球标准时区起点。"},
            {"year": "1964年", "text": "苏联“日出1号”飞船圆满降落，开创人类航天史上首次多人（三人）多舱太空巡航纪录。"}
        ],
        "market_tickers": [
            {"name": "BTC", "price": "$64,250", "change": "+2.85%", "up": True},
            {"name": "ETH", "price": "$2,580", "change": "+1.62%", "up": True},
            {"name": "黄金 (Au)", "price": "$2,658/oz", "change": "+0.42%", "up": True},
            {"name": "纳斯达克", "price": "18,342", "change": "-0.18%", "up": False},
        ],
        "fear_greed": {"index": 71, "text": "贪婪 (Greed)"},
        "news_items": [
            {"tag": "军事", "color": "#EF4444", "content": "海军新型万吨大驱编队圆满完成远海多课目实弹演训，区域防空与立体反潜战力达成新跨越。"},
            {"tag": "航天", "color": "#06B6D4", "content": "我国新一代中型可重复使用液氧甲烷火箭成功完成十公里垂直起降试验，低成本太空运载提速。"},
            {"tag": "Crypto", "color": "#F59E0B", "content": "比特币现货 ETF 单日净流入再破 3.2 亿美元大关，贝莱德与富达机构增持节奏明显加快。"},
            {"tag": "国际", "color": "#3B82F6", "content": "联合国大会通过公海生物多样性保护协定实施细则，正式启动首批公海国际生态红线划定。"},
            {"tag": "防务", "color": "#EF4444", "content": "多国加快推进六代战机隐身协同作战验证，“忠诚僚机”有人/无人编队进入战术试飞阶段。"},
            {"tag": "AI科技", "color": "#8B5CF6", "content": "前沿类脑神经形态计算芯片能效比传统架构跃升逾百倍，支持全端侧离线高阶大模型推理。"},
            {"tag": "Web3", "color": "#F59E0B", "content": "以太坊核心层优化二层网络（Layer2）状态膨胀方案，零知识证明跨链结算确认提速至秒级。"},
            {"tag": "民生", "color": "#10B981", "content": "全国基本医保门诊跨省联网直接结算定点医疗机构突破 60 万家，异地就医报销全面提效。"},
            {"tag": "前沿", "color": "#06B6D4", "content": "深空探测雷达网在近地小行星精确轨道测定上取得新进展，地球防御早期预警能力稳步提升。"},
            {"tag": "监管", "color": "#F59E0B", "content": "欧盟加密资产市场法案（MiCA）资产支持代币细则生效，主流金融机构启动合规支付结算牌照申报。"},
            {"tag": "生态", "color": "#10B981", "content": "中国科考队在南极陆缘冰区测得全新洋流温盐混合异常，为全球气候变暖反馈模型增添核心实测参数。"},
            {"tag": "宏观", "color": "#3B82F6", "content": "国际货币基金组织发布全球展望，上调亚太新兴市场经济体年内增长预期，产业链韧性持续显现。"}
        ],
        "quote": "“历史是未来的密码，科技是丈量未知的尺度，保持对全景世界的敏锐认知。”"
    }

def render_poster(data: dict) -> Image.Image:
    WIDTH = 1080
    PADDING = 54
    CONTENT_WIDTH = WIDTH - PADDING * 2

    f_brand = get_font(FONT_BOLD, 56)
    f_sub = get_font(FONT_REGULAR, 26)
    f_date = get_font(FONT_BOLD, 32)
    f_badge = get_font(FONT_BOLD, 22)
    f_section_title = get_font(FONT_BOLD, 30)
    f_history_text = get_font(FONT_REGULAR, 28)
    f_ticker_name = get_font(FONT_BOLD, 28)
    f_ticker_price = get_font(FONT_BOLD, 34)
    f_ticker_chg = get_font(FONT_REGULAR, 24)
    f_num = get_font(FONT_BOLD, 24)
    f_tag = get_font(FONT_BOLD, 22)
    f_news_text = get_font(FONT_REGULAR, 29)
    f_quote_title = get_font(FONT_BOLD, 26)
    f_quote = get_font(FONT_SERIF_BOLD, 30)
    f_footer = get_font(FONT_REGULAR, 22)

    dummy = Image.new("RGB", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy)

    hist_lines_list = []
    hist_events_total_h = 0
    hist_text_w = CONTENT_WIDTH - 150
    for h in data["history_events"]:
        lines = wrap_text(h["text"], f_history_text, hist_text_w, dummy_draw)
        hist_lines_list.append(lines)
        item_h = len(lines) * 38 + 14
        hist_events_total_h += item_h
    hist_card_h = 70 + hist_events_total_h + 24

    ticker_card_h = 185

    news_lines_list = []
    news_h_total = 0
    news_text_w = CONTENT_WIDTH - 155
    line_h = 44
    for item in data["news_items"]:
        lines = wrap_text(item["content"], f_news_text, news_text_w, dummy_draw)
        news_lines_list.append(lines)
        item_h = len(lines) * line_h + 28
        news_h_total += item_h + 14

    quote_lines = wrap_text(data.get("quote", ""), f_quote, CONTENT_WIDTH - 64, dummy_draw)
    quote_card_h = 70 + len(quote_lines) * 44 + 24

    TOTAL_HEIGHT = 275 + 30 + hist_card_h + 26 + ticker_card_h + 32 + 56 + news_h_total + 20 + quote_card_h + 30 + 85

    img = create_rich_background(WIDTH, TOTAL_HEIGHT)
    draw = ImageDraw.Draw(img)

    header_y = 50
    @app.get("/")
def read_root():
    return {"message": "Hello World"}
