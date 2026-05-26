---
name: ai-frontier-video-pipeline
description: AI 前沿风格短视频制作完整流水线。当用户要求制作AI/科技短视频、生成品牌统一封面和分镜图、渲染带Ken Burns运镜和配乐的短视频时触发。包含品牌模板生成、视频渲染脚本、完整工作流文档，支持从选题到成品交付的一站式操作。
---

# AI 前沿视频制作流水线

## 概述

本 skill 提供「AI前沿」品牌短视频的完整制作流水线，涵盖选题、采集、策划、素材生成、视频渲染、交付六大阶段。品牌视觉规范为暗夜科技蓝，封面和分镜图风格统一，仅需更换文字即可复用。

**触发词示例**：
- "制作一期AI短视频" / "Make an AI short video"
- "生成AI前沿风格视频" / "Generate AI frontier video"
- "渲染视频" / "Render video"
- "生成品牌封面/分镜图"

## 完整工作流

**总预计耗时**：30-45 分钟（不含渲染等待时间）

### Phase 0：选题（预计 2-3 分钟）

**目标**：获取 AI Builder 最新动态，确定本期视频主题

**执行命令模板**：
```bash
# 调用 follow-builders skill
python ~/.workbuddy/skills/follow-builders/scripts/run.py
```

**输出文件**：`output/topic.md`（选题摘要）

**检查点 CP1**：展示 Builder 动态摘要 + 推荐选题方向（3个），等待用户确认

### Phase 1：信息采集（预计 3-5 分钟）

**目标**：采集 AI/科技热点内容，为脚本策划提供原料

**执行命令模板**：
```bash
# 调用 video-content-collector skill
python ~/.workbuddy/skills/video-content-collector/scripts/collect.py --topic "选题主题" --days 7
```

**输出文件**：`output/collected.md`（采集报告，含 5-10 条高质量内容）

### Phase 2：内容策划（预计 5-8 分钟）

**目标**：撰写脚本，设计分镜，输出 JSON 制作包

**输入文件**：`output/collected.md`（采集报告）
**输出文件**：`output/script.json`（JSON 制作包，含旁白文本 + 分镜配置）

**脚本格式要求**：
- 60 秒视频 ≈ 140-160 字旁白
- 分镜数量：4-6 个
- JSON 结构示例见 `assets/slides_ep01_config.json`

**检查点 CP2**：展示完整脚本 + 分镜 JSON + 预计时长，等待用户确认

### Phase 3：素材生成（预计 5-10 分钟）

**目标**：生成品牌统一的分镜图片和封面图

#### 生成分镜图片 — `scripts/slide_template.py`

```bash
# JSON 配置模式（推荐）
python scripts/slide_template.py --config output/script.json --ep 01 --output-dir slides/

# 快速批量模式
python scripts/slide_template.py --titles "开场,要点1,要点2,结尾" --ep 01 --output-dir slides/

# 单张模式
python scripts/slide_template.py --title "标题" --type data --ep 01 --slide 2
```

5种卡片类型：`title`（标题卡）、`point`（要点卡）、`data`（数据卡）、`quote`（引言卡）、`outro`（结尾卡）

**输出文件**：`slides/slide_01_*.png`（6张竖屏 1080x1920 分镜图）

#### 生成封面图 — `scripts/cover_template.py`

```bash
python scripts/cover_template.py --title "视频标题" --ep 01 --output-dir covers/
```

**输出文件**：
- `covers/cover_01_vertical.png`（竖屏 1080x1920）
- `covers/cover_01_horizontal.png`（横屏 1920x1080）

#### TTS 配音 — SenseAudio API

```
Endpoint: /v1/t2a_v2
voice_id: male_0028_a
```

**输出文件**：`output/voice.mp3`（旁白音频，16kHz 单声道）

#### BGM 生成 — SenseAudio Music API

```
1. 调用 /v1/music/lyrics/create 生成结构化歌词
2. 调用 /v1/music/song/create（custom_mode=False, instrumental=True）
3. 轮询 /v1/music/song/pending/{task_id} 获取 audio_url
```

**输出文件**：`output/bgm.mp3`（背景音乐，约 60 秒）

#### ASR 字幕 — SenseAudio API

```
Endpoint: /v1/audio/transcriptions
输入要求：16kHz 单声道 WAV
```

**输出文件**：`output/subtitle.srt`（SRT 字幕文件）

**检查点 CP3**：展示 6 张分镜图片 + 封面图 + 配音波形图，等待用户确认

### Phase 4：视频渲染（预计 10-15 分钟）

**目标**：将分镜图片、配音、BGM、字幕合成最终视频

**输入文件**：
- `slides/slide_01_*.png`（分镜图片）
- `output/voice.mp3`（旁白音频）
- `output/bgm.mp3`（背景音乐，可选）
- `output/subtitle.srt`（字幕文件，可选）

**执行命令模板**：
```bash
python scripts/render_video.py \
  --slides-dir slides/ \
  --voice output/voice.mp3 \
  --bgm output/bgm.mp3 \
  --srt output/subtitle.srt \
  --ep 01 \
  --output output/ep01.mp4
```

**渲染流程**：
1. Ken Burns 运镜（6种预设循环使用：缓推近/缓拉远/缓慢右移/急促推近/扩展揭示/缓慢上移）
2. xfade 转场（fadeblack / smoothright / fade / dissolve，随机选取）
3. 暗角调色（vignette + eq 增强对比度和饱和度）
4. 字幕烧录（NotoSansSC 字号22，MarginV 40，描边2，半透明底色）
5. 音频混流（旁白音量1.0，BGM音量0.12，结尾 fade out 0.8秒）

**自动降级策略**：
- Ken Burns 失败 → 简单推近 → 静态缩放
- xfade 失败 → fade 转场 → concat 拼接
- 字幕烧录失败 → 跳过字幕，输出无字幕版

**输出文件**：`output/ep01.mp4`（最终视频，约 60 秒）

**检查点 CP4**：展示视频文件路径 + 时长 + 文件大小，等待用户确认

### Phase 5：交付（预计 1-2 分钟）

**目标**：整理输出文件，交付给用户

**最终输出结构**：
```
output/
├── ep01.mp4                    # 视频成品
├── covers/
│   ├── cover_01_vertical.png   # 竖屏封面
│   └── cover_01_horizontal.png # 横屏封面
└── slides/
    ├── slide_01_title.png
    ├── slide_02_data.png
    ├── ...
    └── slide_06_outro.png
```

**检查点 CP5**：展示完整输出文件列表，确认交付完成

## 品牌规范

| 项目 | 值 |
|------|-----|
| 品牌名 | AI前沿 |
| 标语 | 第一时间 · 深度解读 |
| 背景渐变 | #080C26 → #160838 |
| 霓虹蓝 | #00D4FF |
| 电紫 | #8B5CF6 |
| 平台规格 | 竖屏 1080x1920 / 横屏 1920x1080 |

## 脚本参考

### `scripts/cover_template.py`

生成品牌统一封面，支持 `--title`、`--ep`、`--date`、`--output-dir` 参数。

### `scripts/slide_template.py`

生成品牌统一分镜图片，支持三种模式：JSON配置 / 快速批量 / 单张生成。

### `scripts/render_video.py`

通用视频渲染器，参数化支持任意 EP 编号，内置 Ken Burns 运镜预设和 xfade 转场。

## 参考资料

### `references/WORKFLOW.md`

完整工作流详细文档，包含环境依赖、目录结构、关键技术参数和踩坑记录。

## 异常处理 & 降级策略

### SenseAudio API 失败

| 场景 | 现象 | 降级方案 |
|---|---|---|
| TTS 失败 | `/v1/t2a_v2` 返回非200 | 提示用户手动提供 MP3，或用系统 `edge-tts` 替代 |
| BGM 生成失败 | lyrics/song API 报错 | 使用无 BGM 版本，或提示用户手动提供 MP3 |
| ASR 失败 | `/v1/audio/transcriptions` 报错 | 手动编写 SRT 字幕，或跳过字幕 |

### FFmpeg 相关问题

| 场景 | 现象 | 处理 |
|---|---|---|
| FFmpeg 找不到 | `shutil.which("ffmpeg")` 返回 None | 提示用户安装 FFmpeg 或用 `--ffmpeg` 指定路径 |
| zoompan 滤镜失败 | Ken Burns 渲染报错 | 脚本自动降级到简单推近 → 静态缩放 |
| xfade 滤镜失败 | 转场合成报错 | 脚本自动降级到 fade → concat 拼接 |
| 字幕烧录失败 | subtitles 滤镜报错 | 脚本自动跳过字幕，输出无字幕版 |

### 依赖缺失

| 依赖 | 检测方式 | 降级/提示 |
|---|---|---|
| Python Pillow | `import PIL` 失败 | 提示 `pip install Pillow` |
| Node.js | `node --version` 失败 | 提示安装 Node.js 22+ |
| follow-builders | skill 不存在 | 提示先安装 follow-builders skill |

### 边界条件覆盖

| 场景 | 现象 | 处理 |
|---|---|---|
| 网络超时 | API 请求 > 30s 无响应 | 重试3次，每次超时翻倍；仍失败则提示用户检查网络 |
| API 限流 | 返回 429 Too Many Requests | 等待 60s 后重试；仍失败则降级到手动提供 |
| 文件格式错误 | 图片非 PNG/JPG、音频非 MP3 | 脚本自动检测格式，不支持则提示用户转换 |
| 磁盘空间不足 | 渲染时写入失败 | 检查输出目录可用空间（需 > 500MB），不足则提示清理 |
| 并发冲突 | 同一 EP 正在渲染 | 检测 `.lock` 文件，存在则提示等待或换 EP 号 |
| 图片分辨率异常 | 非 1080x1920 | 脚本自动 padding/center 到标准尺寸 |
| 音频采样率异常 | 非 16kHz/单声道 | TTS 自动重采样；ASR 前强制重采样 |

### 检查点设计

**重要**：以下每个检查点都**必须暂停并等待用户确认**，不能自主继续执行！

| 检查点 | 暂停时机 | 展示内容 | 继续条件 |
|---|---|---|---|
| **CP1: 选题确认** | Phase 0 完成后 | 展示 Builder 动态摘要 + 推荐选题方向（3个） | 用户说"确认选题"或"继续" |
| **CP2: 脚本确认** | Phase 2 脚本完成后 | 展示完整脚本 + 分镜 JSON + 预计时长 | 用户说"脚本通过"或"继续" |
| **CP3: 素材确认** | Phase 3 素材生成后 | 展示6张分镜图片（竖屏PNG） + 配音波形图 | 用户说"素材OK"或"继续" |
| **CP4: 渲染确认** | Phase 4 渲染完成后 | 展示视频文件路径 + 时长 + 文件大小 | 用户说"交付完成"或"需要修改" |
| **CP5: 封面确认** | 封面生成后 | 展示竖屏+横屏封面PNG | 用户说"封面OK"或"需要调整" |

**异常处理**：
- 用户说"取消" → 回到上一个检查点
- 用户说"修改XX" → 重新执行该步骤
- 用户长时间无响应 → 提示"是否需要帮助？"

## 资源文件

### `assets/`

- `slides_ep01_config.json` — 分镜 JSON 配置示例
- `cover_01_vertical.png` — 竖屏封面示例
- `cover_01_horizontal.png` — 横屏封面示例

## 环境依赖

| 依赖 | 用途 |
|------|------|
| Python 3.13 + Pillow | 品牌模板图片生成 |
| FFmpeg 7.1 | 视频渲染（zoompan / xfade / subtitles 滤镜） |
| Node.js 22+ | follow-builders 技能运行环境 |
| SenseAudio API Key | TTS 配音 + BGM 生成 + ASR 字幕 |

## 关键技术参数

- **TTS voice_id**：`male_0028_a`
- **字幕样式**：字号22，MarginV 40，描边2，底色 `$H80`
- **Ken Burns**：图片预放大1.5x（1620×2880）留缩放空间
- **FFmpeg**：使用系统 PATH 中的 ffmpeg，或通过 `--ffmpeg` 参数指定
- **Python**：使用系统 PATH 中的 python，或通过 `--python` 参数指定
