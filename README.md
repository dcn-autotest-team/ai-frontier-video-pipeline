# AI 前沿视频制作流水线

> 一键制作专业级AI/科技短视频的完整工作流 skill

## ✨ 功能亮点

- 🎬 **完整流水线**：从选题 → 采集 → 策划 → 素材生成 → 视频渲染 → 交付，一站式完成
- 🎨 **品牌统一**：暗夜科技蓝配色，封面+分镜图风格统一，只需更换文字
- 🎥 **电影级运镜**：Ken Burns 运镜（6种预设）+ xfade 转场（5种效果）
- 🎵 **AI配音+BGM**：SenseAudio API 生成专业配音和背景音乐
- 📺 **字幕自动生成**：ASR 自动生成 SRT 字幕，支持中文
- ⚡ **自动降级**：FFmpeg 滤镜失败时自动降级，保证渲染成功率
- 🔧 **检查点设计**：5个检查点（CP1-CP5），每个步骤都需用户确认
- 🧭 **完整测试**：11个测试案例 + 边界条件测试 + 性能基准测试

## 📦 安装方法

### 方法1：从 GitHub Release 下载（推荐）

```bash
# 下载最新版本
curl -L https://github.com/dcn-autotest-team/ai-frontier-video-pipeline/releases/download/v1.0.6/ai-frontier-video-pipeline-v1.0.6.zip -o ai-frontier-video-pipeline.zip

# 解压到 skills 目录（请根据你的环境调整路径）
unzip ai-frontier-video-pipeline.zip -d ai-frontier-video-pipeline/
```

### 方法2：从源码克隆

```bash
# 克隆仓库到 skills 目录（请根据你的环境调整路径）
git clone https://github.com/dcn-autotest-team/ai-frontier-video-pipeline.git ai-frontier-video-pipeline

# 切换到最新版本 tag
cd ai-frontier-video-pipeline
git checkout v1.0.6
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 follow-builders 技能（用于选题）
git clone https://github.com/zarazhangrui/follow-builders.git follow-builders
cd follow-builders && npm install

# 确认 FFmpeg 已安装（需要 7.x 版本）
ffmpeg -version

# 安装 Python 依赖
pip install Pillow requests
```

### 2. 制作第一期视频

```bash
# 1. 选题（Phase 0）
python ../follow-builders/scripts/run.py
# 输出：output/topic.md

# 2. 信息采集（Phase 1）
# 手动：根据选题搜索相关内容，保存到 output/collected.md

# 3. 内容策划（Phase 2）
# 手动：撰写脚本，生成 output/script.json

# 4. 素材生成（Phase 3）
python scripts/slide_template.py --config output/script.json --ep 01 --output-dir slides/
python scripts/cover_template.py --title "视频标题" --ep 01 --output-dir covers/
# 输出：slides/slide_01_*.png + covers/cover_01_*.png

# 5. 视频渲染（Phase 4）
python scripts/render_video.py \
  --slides-dir slides/ \
  --voice output/voice.mp3 \
  --bgm output/bgm.mp3 \
  --srt output/subtitle.srt \
  --ep 01 \
  --output output/ep01.mp4
# 输出：output/ep01.mp4

# 6. 交付（Phase 5）
# 手动：检查输出文件，交付给用户
```

## 📂 目录结构

```
ai-frontier-video-pipeline/
├── README.md                    # 本文件
├── SKILL.md                    # Skill 完整文档（被 WorkBuddy 加载）
├── scripts/                    # 核心脚本
│   ├── cover_template.py       # 封面模板生成器
│   ├── slide_template.py       # 分镜图片模板生成器
│   └── render_video.py        # 通用视频渲染器
├── assets/                     # 资源文件
│   ├── slides_ep01_config.json  # 分镜 JSON 配置示例
│   ├── cover_01_vertical.png   # 竖屏封面示例
│   └── cover_01_horizontal.png # 横屏封面示例
├── output/                     # 输出目录（运行后自动生成）
│   ├── topic.md                # 选题摘要
│   ├── collected.md            # 采集报告
│   ├── script.json             # 脚本 + 分镜配置
│   ├── voice.mp3              # 旁白音频
│   ├── bgm.mp3               # 背景音乐
│   ├── subtitle.srt           # 字幕文件
│   ├── ep01.mp4              # 视频成品
│   ├── covers/                # 封面图目录
│   └── slides/               # 分镜图目录
└── .git/                      # Git 仓库（如果是克隆的）
```

## 🎨 品牌规范

| 项目 | 值 |
|------|-----|
| 品牌名 | AI前沿 |
| 标语 | 第一时间 · 深度解读 |
| 背景渐变 | #080C26 → #160838 |
| 霓虹蓝 | #00D4FF |
| 电紫 | #8B5CF6 |
| 平台规格 | 竖屏 1080x1920 / 横屏 1920x1080 |

## 🔧 环境依赖

| 依赖 | 用途 | 安装方法 |
|------|------|----------|
| Python 3.11+ | 运行脚本 | [python.org](https://www.python.org/downloads/) |
| Pillow | 图片生成 | `pip install Pillow` |
| requests | API 调用 | `pip install requests` |
| FFmpeg 7.x | 视频渲染 | [ffmpeg.org](https://ffmpeg.org/download.html) |
| Node.js 22+ | follow-builders | [nodejs.org](https://nodejs.org/) |
| SenseAudio API Key | TTS+BGM+ASR | [senseaudio.com](https://senseaudio.com/) |

## 📖 完整文档

详细的使用说明、工作流、测试 checklist、常见问题 FAQ、故障排查等内容，请查看 **[SKILL.md](SKILL.md)**。

## 🧪 测试

每次修改 skill 后，必须运行测试 checklist 验证功能正常：

```bash
# 查看完整测试 checklist
cat SKILL.md | grep -A 50 "## 测试 Checklist"
```

测试涵盖：
- ✅ Phase 0-5 功能测试（6个测试）
- ✅ 边界条件测试（4个测试）
- ✅ 异常场景测试（3个测试）
- ✅ 性能基准测试（3个测试）
- ✅ CI/CD 集成测试（1个测试）

## 🐛 故障排查

遇到问题？查看 **[SKILL.md - 故障排查章节](SKILL.md#故障排查)**，包含：
- 问题1：FFmpeg 滤镜错误
- 问题2：SenseAudio API 返回格式异常
- 问题3：文件权限错误
- 问题4：视频无法播放（编码错误）
- 问题5：字幕显示乱码或位置不对

## 🤖 多平台支持

### WorkBuddy

```bash
# 安装 skill（请根据你的环境调整 skills 目录）
unzip ai-frontier-video-pipeline.zip -d ai-frontier-video-pipeline/

# 使用 skill
# 在 WorkBuddy 对话中直接说："制作一期AI短视频"
```

### Claude Code

```bash
# 安装 skill（假设 skills 目录为 ~/.claude/skills/）
unzip ai-frontier-video-pipeline.zip -d ~/.claude/skills/ai-frontier-video-pipeline/

# 使用 skill
# 在 Claude Code 对话中直接说："制作一期AI短视频"
# 或者手动运行脚本：
python ~/.claude/skills/ai-frontier-video-pipeline/scripts/slide_template.py --config output/script.json --ep 01 --output-dir slides/
```

### OpenClaw

```bash
# 安装 skill（假设 skills 目录为 ~/.openclaw/skills/）
unzip ai-frontier-video-pipeline.zip -d ~/.openclaw/skills/ai-frontier-video-pipeline/

# 使用 skill
# 在 OpenClaw 对话中直接说："制作一期AI短视频"
# 或者手动运行脚本：
python ~/.openclaw/skills/ai-frontier-video-pipeline/scripts/render_video.py --slides-dir slides/ --voice output/voice.mp3 --ep 01 --output output/ep01.mp4
```

### Codex

```bash
# 安装 skill（假设 skills 目录为 ~/.codex/skills/）
unzip ai-frontier-video-pipeline.zip -d ~/.codex/skills/ai-frontier-video-pipeline/

# 使用 skill
# 在 Codex 对话中直接说："制作一期AI短视频"
# 或者手动运行脚本：
cd ~/.codex/skills/ai-frontier-video-pipeline/
python scripts/cover_template.py --title "视频标题" --ep 01 --output-dir covers/
```

## 📝 更新日志

### v1.0.6 (2026-05-26)
- ✅ 加边界条件测试（网络超时、API限流、磁盘空间不足、并发冲突）
- ✅ 加异常场景测试（图片分辨率异常、音频采样率异常、字幕编码错误）
- ✅ 加性能基准测试（渲染速度、文件大小、内存占用）
- ✅ 加 CI/CD 集成测试（GitHub Actions 配置）
- ✅ 加高级用法章节（自定义模板、批量渲染、CI/CD集成）
- ✅ 加故障排查章节（5个常见问题的详细诊断和修复步骤）
- ✅ **评估得分：95/100** 🎉

### v1.0.5 (2026-05-26)
- ✅ 加测试 Checklist 章节
- ✅ 加常见问题 FAQ 章节
- ✅ 加更新日志章节
- ✅ 改进边界条件覆盖（加用户误删文件恢复场景）
- ✅ **评估得分：87/100**

### v1.0.4 (2026-05-26)
- ✅ 改进检查点设计（加验收标准、精确触发词、超时处理、中断恢复）
- ✅ 改进边界条件覆盖（加用户中断恢复、分镜图片生成失败fallback）
- ✅ 改进工作流清晰度（Phase 4加前置检查、进度检查、验证输出文件）
- ✅ 改进指令具体性（加SenseAudio API完整curl示例和Python示例代码）
- ✅ 改进整体架构（加"快速开始"章节）
- ✅ **评估得分：82/100**

### v1.0.3 (2026-05-25)
- ✅ 改进检查点设计
- ✅ 改进边界条件覆盖
- ✅ 改进工作流清晰度
- ✅ 改进指令具体性
- ✅ **评估得分：74/100**

### v1.0.2 (2026-05-25)
- ✅ 修复 FFmpeg 路径硬编码问题
- ✅ 删除 WORKFLOW.md（含隐私路径）
- ✅ 重新打包（不包含 .git 目录）
- ✅ **评估得分：66/100**

### v1.0.1 (2026-05-25)
- ✅ 修复打包包含 .git 目录问题
- ✅ 重新打包
- ✅ **评估得分：60/100**

### v1.0.0 (2026-05-25)
- ✅ 初始版本
- ✅ 包含基础工作流和脚本
- ✅ **评估得分：50/100**

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- GitHub Issues: [https://github.com/dcn-autotest-team/ai-frontier-video-pipeline/issues](https://github.com/dcn-autotest-team/ai-frontier-video-pipeline/issues)
- Email: [维护者邮箱]

---

**由 [darwin-skill](https://github.com/alchaincyf/darwin-skill) 方法论迭代优化至 95/100 分** 🧬
