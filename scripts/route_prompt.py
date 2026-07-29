#!/usr/bin/env python3
"""为短剧/电影分镜提示词生成路由摘要。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FORMAT_KEYWORDS = {
    "vertical-short": [
        "9:16",
        "竖屏",
        "竖版",
        "手机",
        "抖音",
        "快手",
        "小红书",
        "reels",
        "shorts",
        "tiktok",
    ],
    "horizontal-short": [
        "横版短剧",
        "横屏短剧",
        "16:9短剧",
        "b站横版短剧",
        "横版剧",
        "横屏剧",
        "横版",
        "横屏",
        "16:9",
        "b站横版",
    ],
    "horizontal-film": ["横版电影", "电影分镜", "预告片", "长片", "影视片段", "宽屏电影"],
}

STYLE_KEYWORDS = {
    "live-action": ["真人", "仿真人", "实拍", "真人剧", "电视剧", "电影级", "photoreal"],
    "3d-animation": [
        "3d",
        "3D",
        "三维",
        "cg",
        "CG",
        "虚幻",
        "游戏电影",
        "动画电影",
        "国漫",
        "3D国漫",
        "三维国风",
        "3D短剧",
        "3D竖版短剧",
        "c4d",
        "C4D",
        "oc渲染",
        "OC渲染",
        "ue5",
        "UE5",
        "影视光影",
    ],
    "2d-anime": ["2d", "2D", "二维", "日漫", "日式", "番剧", "赛璐璐", "动漫", "漫画"],
}

GUOMAN_3D_KEYWORDS = [
    "国漫",
    "3D国漫",
    "三维国风",
    "3D竖版短剧",
    "c4d",
    "C4D",
    "oc渲染",
    "OC渲染",
    "ue5",
    "UE5",
    "影视光影",
]

EXPLICIT_FILM_ROUTE_KEYWORDS = FORMAT_KEYWORDS["horizontal-film"]
EXPLICIT_HORIZONTAL_SHORT_KEYWORDS = [
    "横版短剧",
    "横屏短剧",
    "16:9短剧",
    "b站横版短剧",
    "横版剧",
    "横屏剧",
]
HORIZONTAL_ASPECT_KEYWORDS = ["横版", "横屏", "16:9", "b站横版"]
VERTICAL_ROUTE_KEYWORDS = FORMAT_KEYWORDS["vertical-short"]
EXPLICIT_2D_STYLE_KEYWORDS = ["2d", "二维", "日漫", "日式", "番剧", "赛璐璐", "漫画"]
EXPLICIT_3D_STYLE_KEYWORDS = [
    "3d",
    "三维",
    "cg",
    "虚幻",
    "游戏电影",
    "动画电影",
    "国漫",
    "c4d",
    "oc渲染",
    "ue5",
    "影视光影",
]


def read_text(args: argparse.Namespace) -> str:
    chunks: list[str] = []
    if args.script:
        chunks.append(args.script)
    if args.script_file:
        chunks.append(Path(args.script_file).read_text(encoding="utf-8"))
    return "\n".join(chunks)


def score_route(text: str, table: dict[str, list[str]]) -> dict[str, int]:
    lower = text.lower()
    scores: dict[str, int] = {}
    for route, keywords in table.items():
        score = 0
        for keyword in keywords:
            score += len(re.findall(re.escape(keyword.lower()), lower))
        scores[route] = score
    return scores


def choose(value: str, text: str, table: dict[str, list[str]], default: str) -> tuple[str, dict[str, int]]:
    if value != "auto":
        return value, score_route(text, table)
    scores = score_route(text, table)
    winner, score = max(scores.items(), key=lambda item: item[1])
    if score <= 0:
        return default, scores
    return winner, scores


def choose_format_route(value: str, text: str) -> tuple[str, dict[str, int]]:
    scores = score_route(text, FORMAT_KEYWORDS)
    if value != "auto":
        return value, scores

    # Explicit film-route words win over generic 16:9 or horizontal aspect hints.
    # "电影感/电影级质感" is intentionally not here: it describes texture, not route.
    if has_keyword(text, EXPLICIT_FILM_ROUTE_KEYWORDS):
        return "horizontal-film", scores
    if has_keyword(text, EXPLICIT_HORIZONTAL_SHORT_KEYWORDS) or has_keyword(text, HORIZONTAL_ASPECT_KEYWORDS):
        return "horizontal-short", scores
    if has_keyword(text, VERTICAL_ROUTE_KEYWORDS):
        return "vertical-short", scores
    if "短剧" in text:
        return "vertical-short", scores
    return "vertical-short", scores


def choose_style_route(value: str, text: str) -> tuple[str, dict[str, int]]:
    scores = score_route(text, STYLE_KEYWORDS)
    if value != "auto":
        return value, scores

    # Explicit 2D wording wins over generic "国漫"; plain "国漫" remains 3D by default.
    if has_keyword(text, EXPLICIT_2D_STYLE_KEYWORDS):
        return "2d-anime", scores
    if has_keyword(text, EXPLICIT_3D_STYLE_KEYWORDS):
        return "3d-animation", scores
    if has_keyword(text, STYLE_KEYWORDS["live-action"]):
        return "live-action", scores
    if "动漫" in text:
        return "2d-anime", scores
    return "live-action", scores


def infer_format_from_aspect(aspect: str, text: str) -> str:
    if aspect == "9:16":
        return "vertical-short"
    if aspect == "16:9":
        film_scores = score_route(text, {"horizontal-film": FORMAT_KEYWORDS["horizontal-film"]})
        if film_scores["horizontal-film"] > 0:
            return "horizontal-film"
        return "horizontal-short"
    return "auto"


def has_keyword(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def references_for(format_route: str, style: str, text: str = "") -> list[str]:
    refs = [
        "references/routing.md",
        "references/output-format.md",
        "references/format-routes.md",
        "references/camera-rules.md",
        "references/visual-styles.md",
    ]
    if format_route == "vertical-short" and style == "live-action":
        refs.insert(1, "references/vertical-9x16-live-action.md")
    if format_route == "vertical-short" and style == "3d-animation" and has_keyword(text, GUOMAN_3D_KEYWORDS):
        refs.insert(1, "references/vertical-9x16-3d-guoman.md")
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description="把场景/剧本需求路由到对应分镜提示词规则。")
    parser.add_argument("--script", default="", help="Inline script or request text.")
    parser.add_argument("--script-file", help="UTF-8 text file containing script or request text.")
    parser.add_argument("--format", choices=["auto", "vertical-short", "horizontal-short", "horizontal-film"], default="auto")
    parser.add_argument("--aspect", choices=["auto", "9:16", "16:9"], default="auto", help="Backward-compatible aspect hint.")
    parser.add_argument("--style", choices=["auto", "live-action", "3d-animation", "2d-anime"], default="auto")
    parser.add_argument("--scene-images", type=int, default=0, help="Number of uploaded scene images.")
    args = parser.parse_args()

    text = read_text(args)
    format_hint = args.format
    if format_hint == "auto" and args.aspect != "auto":
        format_hint = infer_format_from_aspect(args.aspect, text)
    format_route, format_scores = choose_format_route(format_hint, text)
    style, style_scores = choose_style_route(args.style, text)

    print(f"选定路线: {format_route} + {style}")
    print(f"场景图片数量: {args.scene_images}")
    print(f"成片路线得分: {format_scores}")
    print(f"视觉风格得分: {style_scores}")
    print("建议读取这些参考文件:")
    for ref in references_for(format_route, style, text):
        print(f"- {ref}")
    print("检查清单:")
    print("- 只使用剧本和当前剧本场景图片确定后续生成逻辑。")
    print("- 保留剧本事实；场景图片用于场景、站位、光源、道具、镜头调度和连续性。")
    print("- 按固定外壳输出：每组先写场景提示，再写逐镜视频提示词，不输出 prompt/video_prompt 标签。")
    print("- 人物统一标记为 @角色名；视频提示词不重复图片锁定的外貌。")
    print("- 抽象情绪必须转译为可见微表情和微动作。")
    print("- 先识别信息、情绪、关系、距离或动作结果变化，再决定是否使用特殊镜头；普通对白保持自然覆盖。")
    print("- 在内部区分距离、大小、空间、方向、视角、信息、节奏冲击与静态张力，并按1至4级控制强度。")
    print("- 明显冲击或爆点镜头必须检查轴线、动作因果、空间连续、透视形变和AI稳定性，必要时使用稳妥替代。")
    print("- 爆点台词、揭露、反转、威胁和告白后只安排有新信息的反应或动作结果，不补无意义反应镜头。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
