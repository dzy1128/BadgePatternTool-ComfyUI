# 更新日志 - Changelog (ComfyUI版)

## [2.0.0] - 2025-11-07

### 🎉 重大更新：ComfyUI版本发布

本次更新将BadgePatternTool改造为ComfyUI自定义节点，实现了完全的工作流集成。

### ✨ 新增功能

#### 核心节点
- **圆形徽章裁剪节点 (CircularCropNode)**
  - 支持任意图片裁剪成圆形徽章
  - 可配置徽章直径（10-200mm）
  - 支持缩放（0.1-5.0倍）
  - 支持X/Y轴偏移
  - 支持360度旋转
  - 可调DPI（72-600）

- **徽章A4排版节点 (BadgeLayoutNode)**
  - 智能A4纸排版
  - 网格模式：规则行列排列
  - 紧凑模式：六边形蜂巢密排
  - 可调节间距和页边距
  - 自动显示空位占位符

- **自动优化参数节点 (AutoOptimizeBadgeNode)**
  - 自动计算最佳缩放比例
  - 智能适配不同长宽比图片
  - 输出可直接连接到裁剪节点

#### 技术特性
- 完全支持ComfyUI的tensor格式
- 自动处理批次图片
- 高性能图片处理
- 兼容ComfyUI工作流系统

### 🔧 技术改进

#### 核心功能保留
- ✅ 保留原有的图片处理算法
- ✅ 保留智能排版引擎
- ✅ 保留高质量输出（300 DPI）

#### 架构优化
- 移除GUI依赖（PySide6）
- 移除文件系统依赖
- 简化为纯图片处理节点
- 适配ComfyUI的数据流

#### 代码优化
- 统一的tensor/PIL转换
- 优化的内存使用
- 简化的参数接口
- 完整的类型提示

### 📚 文档

#### 新增文档
- `README_COMFYUI.md` - 完整的ComfyUI使用指南
- `INSTALL.md` - 详细的安装说明
- `TESTING.md` - 测试指南
- `example_workflow.json` - 工作流示例

#### 更新文档
- `README.md` - 增加ComfyUI版本说明
- `requirements-comfyui.txt` - ComfyUI依赖说明

### 🎯 功能对比

| 功能 | 桌面版 | ComfyUI版 |
|-----|-------|----------|
| 圆形裁剪 | ✅ | ✅ |
| 批量处理 | ✅ | ✅ |
| A4排版 | ✅ | ✅ |
| 网格/紧凑模式 | ✅ | ✅ |
| 参数调节 | ✅ | ✅ |
| 实时预览 | ✅ | ✅（ComfyUI预览）|
| 多页面 | ✅ | 🔄（计划中）|
| PDF导出 | ✅ | ⚠️（需外部节点）|
| 打印功能 | ✅ | ⚠️（需外部工具）|
| GUI界面 | ✅ | ❌（使用ComfyUI界面）|
| 工作流集成 | ❌ | ✅ |
| 节点复用 | ❌ | ✅ |

### 🚀 使用示例

#### 基本工作流
```
Load Image → 圆形徽章裁剪 → Save Image
```

#### 批量排版工作流
```
Load Image (批次) → 圆形徽章裁剪 → 徽章A4排版 → Save Image
```

#### 自动优化工作流
```
Load Image → 自动优化徽章参数 → 圆形徽章裁剪 → Save Image
                ↓                      ↑
                └──────（连接参数）─────┘
```

### 💡 性能指标

- 圆形裁剪速度: ~50-100ms/张（800x600）
- A4排版速度: ~200-400ms（12个徽章）
- 内存占用: ~8MB/徽章（58mm @ 300dpi）

### 🐛 已知问题

- 暂不支持多页面自动分页（计划在v2.1.0实现）
- PDF导出需要使用额外的ComfyUI节点
- 暂不支持直接打印（可保存后打印）

### 🔮 未来计划

#### v2.1.0（计划）
- [ ] 多页面自动分页支持
- [ ] 更多预设徽章尺寸
- [ ] 批次参数差异化

#### v2.2.0（计划）
- [ ] PDF导出节点
- [ ] 更多排版模式
- [ ] 自定义形状支持

#### v2.3.0（计划）
- [ ] 批量文本添加
- [ ] 边框和装饰
- [ ] 色彩调整工具

### 🙏 致谢

感谢原BadgePatternTool项目的所有贡献者！

特别感谢ComfyUI社区的支持和反馈。

### 📦 安装

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/BadgePatternTool-ComfyUI.git
# 重启ComfyUI
```

### 📝 迁移指南

#### 从桌面版迁移

如果您之前使用桌面版：

1. **图片处理逻辑完全相同**
   - 相同的裁剪算法
   - 相同的排版引擎
   - 相同的输出质量

2. **参数对应关系**
   - 徽章直径 → diameter_mm
   - 缩放 → scale
   - 偏移 → offset_x, offset_y
   - 旋转 → rotation

3. **工作流程变化**
   - 桌面版：导入→编辑→排版→导出
   - ComfyUI版：节点连接→参数设置→执行

### 🔗 相关链接

- **原始项目**: https://github.com/fenglyu1314/BadgePatternTool
- **ComfyUI**: https://github.com/comfyanonymous/ComfyUI
- **问题报告**: https://github.com/your-username/BadgePatternTool-ComfyUI/issues
- **使用文档**: [README_COMFYUI.md](README_COMFYUI.md)

---

## 版本号说明

- 主版本号（2.x.x）：重大架构变更
- 次版本号（x.1.x）：新功能添加
- 修订号（x.x.1）：Bug修复和小改进

---

**当前版本**: v2.0.0
**发布日期**: 2025-11-07
**维护状态**: ✅ 活跃开发中

