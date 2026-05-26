# AI前沿 — 视频制作完整工作流

> 从选题到成品，一站式流程。品牌风格：暗夜科技蓝，封面+视频图片统一，只换文字。

## 工作流总览

```
Phase 0: 选题 ───→ follow-builders 技能获取AI Builder动态
Phase 1: 采集 ───→ 灵阅采集 + AIHOT 热点查询
Phase 2: 策划 ───→ 灵枢写脚本+分镜
Phase 3: 素材 ───→ 品牌模板生成图 + TTS配音 + BGM
Phase 4: 渲染 ───→ FFmpeg 通用渲染器
Phase 5: 交付 ───→ 封面+视频成品
```

## Phase 0: 选题（follow-builders）

使用 `follow-builders` 技能获取AI领域一线建设者动态：

```bash
# 触发方式（对话中）
"帮我获取AI Builder最新动态"
"看看Karpathy最近说了什么"
"follow builders digest"
```

数据来源：
- 25位AI Builder的X/Twitter精选推文
- 6个热门AI播客（Latent Space、Training Data等）
- Anthropic/Claude官方博客
- 无需API Key，中心化每日更新

## Phase 1: 采集（灵阅 + AIHOT）

**灵阅采集**：视频生成团队的灵阅Agent负责全网采集
```bash
# 触发方式
"帮我采集XX主题的资讯"
```

**AIHOT 热点查询**：快速获取当日AI资讯
```bash
# 触发方式
"今天AI圈有什么"
"AI HOT"
```

## Phase 2: 策划（灵枢）

灵枢根据采集内容，策划一期视频：
- 筛选选题（1个核心主题）
- 写脚本（60秒≈140-160字旁白）
- 设计分镜（4-6个分镜）
- 输出JSON制作包

## Phase 3: 素材生成

### 3a. 分镜图片（品牌模板）

```bash
# JSON配置模式（最灵活）
python artifacts/slide_template.py --config slides_config.json --ep 01 --output-dir output/slides/

# 快速批量模式
python artifacts/slide_template.py --titles "开场,要点1,要点2,结尾" --ep 01 --output-dir output/slides/
```

5种卡片类型：
| 类型 | 用途 | 关键参数 |
|------|------|---------|
| title | 开场/大标题 | title, subtitle |
| data | 数据亮点展示 | title, data_items[{value, label}] |
| point | 要点列表 | title, points[] |
| quote | 金句/人物语录 | quote, author |
| outro | 结尾品牌卡 | （无额外参数） |

### 3b. 封面图

```bash
python artifacts/cover_template.py --title "视频标题" --ep 01 --output-dir output/covers/
```

输出：竖屏(1080x1920) + 横屏(1920x1080)

### 3c. TTS配音（SenseAudio）

```bash
# API: /v1/t2a_v2
# voice_id: male_0028_a
```

### 3d. BGM（SenseAudio Music）

```bash
# 1. 先用 /v1/music/lyrics/create 生成结构化歌词
# 2. 再传 custom_mode=False + instrumental=True 生成纯音乐
```

### 3e. ASR字幕（SenseAudio）

```bash
# API: /v1/audio/transcriptions
# 输入：16kHz单声道WAV
```

## Phase 4: 视频渲染

```bash
python artifacts/render_video.py \
  --slides-dir output/slides/ \
  --voice output/voice.mp3 \
  --bgm output/bgm.mp3 \
  --srt output/subtitle.srt \
  --ep 01 \
  --output output/ep01.mp4
```

渲染流程：
1. Ken Burns运镜（6种预设：推近/平移/拉远/急推/扩展/上行）
2. xfade交叉淡入淡出转场（fadeblack/smoothright/fade/dissolve）
3. 暗角调色（vignette + eq增强）
4. 字幕烧录（NotoSansSC 30px + 半透明底 + 描边）
5. 音频混流（旁白1.0 + BGM 0.12 + fade out）

自动降级策略：
- Ken Burns失败 → 简单推近 → 静态缩放
- xfade失败 → fade转场 → concat拼接
- 字幕失败 → 无字幕版

## Phase 5: 交付

最终输出清单：
```
output/
├── ep01.mp4              # 视频成品
├── covers/
│   ├── cover_01_vertical.png    # 竖屏封面
│   └── cover_01_horizontal.png  # 横屏封面
└── slides/
    ├── slide_01_title.png       # 分镜图片
    ├── slide_02_data.png
    ├── ...
    └── slide_06_outro.png
```

## 品牌规范

- **品牌名**：AI前沿
- **标语**：第一时间 · 深度解读
- **配色**：暗夜科技蓝
  - 背景渐变：#080C26 → #160838
  - 霓虹蓝：#00D4FF
  - 电紫：#8B5CF6
- **视觉元素**：渐变背景 + 扫描线 + 电路线条 + 六边形网格 + 粒子 + 霓虹辉光
- **平台**：全平台（竖屏 1080x1920 + 横屏 1920x1080）

## 目录结构

```
artifacts/
├── cover_template.py         # 封面模板生成器
├── slide_template.py         # 分镜图片模板生成器
├── render_video.py           # 通用视频渲染器
├── covers/                   # 封面图输出
├── slides_branded/           # 分镜图输出
└── _archive/                 # 归档（旧版本/中间产物）
```

## 环境依赖

| 依赖 | 说明 |
|------|------|
| Python 3.13 + Pillow | 品牌模板生成 |
| FFmpeg 7.1 | 视频渲染（内置路径） |
| Node.js 22+ | follow-builders 技能 |
| SenseAudio API | TTS + BGM + ASR |
