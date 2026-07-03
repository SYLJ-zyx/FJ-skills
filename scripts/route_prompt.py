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
    "horizontal-short": ["横版短剧", "横屏短剧", "16:9短剧", "b站横版短剧", "横版剧", "横屏剧"],
    "horizontal-film": ["横版电影", "电影分镜", "电影感", "预告片", "长片", "影视片段", "宽屏电影"],
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
        "3D国漫",
        "国漫建模",
        "古风国漫",
        "精细建模",
        "角色建模精细",
        "3D国风",
    ],
    "2d-anime": ["2d", "2D", "二维", "日漫", "日式", "番剧", "赛璐璐", "动漫", "漫画"],
}


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


def infer_format_from_aspect(aspect: str, text: str) -> str:
    if aspect == "9:16":
        return "vertical-short"
    if aspect == "16:9":
        film_scores = score_route(text, {"horizontal-film": FORMAT_KEYWORDS["horizontal-film"]})
        if film_scores["horizontal-film"] > 0:
            return "horizontal-film"
        return "horizontal-short"
    return "auto"


def references_for(format_route: str, style: str) -> list[str]:
    refs = [
        "references/routing.md",
        "references/output-format.md",
        "references/format-routes.md",
        "references/camera-rules.md",
        "references/visual-styles.md",
    ]
    if format_route == "vertical-short" and style == "live-action":
        refs.insert(1, "references/vertical-9x16-live-action.md")
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
    format_route, format_scores = choose(format_hint, text, FORMAT_KEYWORDS, "vertical-short")
    style, style_scores = choose(args.style, text, STYLE_KEYWORDS, "live-action")

    print(f"选定路线: {format_route} + {style}")
    print(f"场景图片数量: {args.scene_images}")
    print(f"成片路线得分: {format_scores}")
    print(f"视觉风格得分: {style_scores}")
    print("建议读取这些参考文件:")
    for ref in references_for(format_route, style):
        print(f"- {ref}")
    print("检查清单:")
    print("- 只使用剧本和当前剧本场景图片确定后续生成逻辑。")
    print("- 保留剧本事实；场景图片用于场景、站位、光源、道具、镜头调度和连续性。")
    print("- 先输出 prompt，再输出 video_prompt，并放入固定外壳。")
    print("- 人物统一标记为 @角色名；视频提示词不重复图片锁定的外貌。")
    print("- 抽象情绪必须转译为可见微表情和微动作。")
    print("- 爆点台词、揭露、反转、威胁和告白后必须安排反应镜头。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
