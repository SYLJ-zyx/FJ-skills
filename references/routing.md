# 路由规则

## 输入读取

只收集两类必需输入：剧本文本、当前剧本的场景图片。剧本文本是剧情事实的唯一来源。场景图片用于识别地点质感、空间层次、光源方向、关键道具、人物站位、镜头调度基础和连续性。不要把其他资料作为必需输入；用户主动提供时可以参考，但不得强制追问。

## 成片路线

- `vertical-short`：竖版短剧，9:16，手机端优先，强钩子、强反应、快节奏。
- `horizontal-short`：横版短剧，16:9，保留短剧爽点和快速推进，但允许更多横向站位与环境信息。
- `horizontal-film`：横版电影，16:9，偏电影分镜、段落调度、镜头组和空间叙事。
- `auto`：根据用户词汇自动判断。若只说短剧且未明确横版，默认 `vertical-short`。

## 视觉风格

- `live-action`：真人、仿真人、实拍、真人剧、真人电视剧、电影级真人质感。
- `3d-animation`：3D、3D国漫、国漫建模、古风国漫、精细建模、三维、CG、游戏电影感、三维动画电影质感。
- `2d-anime`：2D、二维、日漫、日式动画、赛璐璐、漫画动态分镜。
- `auto`：根据用户词汇和图片类型自动判断。若用户提供真人照片并说短剧，默认 `live-action`；若用户只说竖版短剧、短剧、真人短剧格式或提供现实题材剧本但未指定动画风格，也默认 `live-action`。

## 路由矩阵

| 路线 | 应读取的主要规则 |
| --- | --- |
| `vertical-short + live-action` | `vertical-9x16-live-action.md`、`format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md` |
| `vertical-short + 3d-animation` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；套用竖版短剧镜头与3D动画表演规则；用户要求3D国漫/古风国漫/精细建模时执行 `visual-styles.md` 的“3D国漫精细建模短剧” |
| `vertical-short + 2d-anime` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；套用竖版短剧镜头与日漫竖向分镜规则 |
| `horizontal-short + live-action` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；横版短剧镜头但仍保持爆点节奏 |
| `horizontal-short + 3d-animation` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；横版短剧节奏加3D动画镜头 |
| `horizontal-short + 2d-anime` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；横版短剧节奏加日漫镜头语言 |
| `horizontal-film + live-action` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；电影式段落、空间、光影和镜头组 |
| `horizontal-film + 3d-animation` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；电影式3D场景调度 |
| `horizontal-film + 2d-anime` | `format-routes.md`、`camera-rules.md`、`visual-styles.md`、`output-format.md`；电影式日漫分镜和镜头停顿 |

## 缺失信息处理

能从用户描述推断时直接执行。只有在成片路线和视觉风格都无法判断，且不同选择会明显改变输出时，才追问最多两个问题：

- 成片路线：竖版短剧、横版短剧、横版电影？
- 视觉风格：真人/仿真人、3D动画、日漫2D？
