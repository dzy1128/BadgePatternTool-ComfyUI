# 安装指南 - Installation Guide

## 快速安装 Quick Install

### 步骤1：定位ComfyUI自定义节点目录

找到您的ComfyUI安装目录下的 `custom_nodes` 文件夹：

```
ComfyUI/
└── custom_nodes/
    └── (在这里安装)
```

### 步骤2：安装节点

#### 方法A：使用Git（推荐）

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/BadgePatternTool-ComfyUI.git
```

#### 方法B：手动下载

1. 下载此仓库的ZIP文件
2. 解压到 `ComfyUI/custom_nodes/` 目录
3. 确保文件夹名为 `BadgePatternTool-ComfyUI`

### 步骤3：重启ComfyUI

关闭并重新启动ComfyUI。

### 步骤4：验证安装

在ComfyUI中：
1. 右键点击画布
2. 在节点菜单中查找 "徽章工具" 分类
3. 应该能看到以下节点：
   - 圆形徽章裁剪
   - 徽章A4排版
   - 自动优化徽章参数

## 依赖说明 Dependencies

本节点使用ComfyUI的标准依赖，无需额外安装：

- ✅ torch (ComfyUI自带)
- ✅ numpy (ComfyUI自带)
- ✅ PIL/Pillow (ComfyUI自带)

## 文件结构 File Structure

安装完成后的文件结构应该是：

```
ComfyUI/custom_nodes/BadgePatternTool-ComfyUI/
├── __init__.py              # 节点注册文件
├── nodes.py                 # 节点实现
├── README_COMFYUI.md        # 使用说明
├── INSTALL.md               # 安装指南（本文件）
├── example_workflow.json    # 工作流示例
└── requirements-comfyui.txt # 依赖列表（参考）
```

## 故障排除 Troubleshooting

### 问题：节点没有出现在菜单中

**解决方案：**
1. 确认文件夹名称正确：`BadgePatternTool-ComfyUI`
2. 检查 `__init__.py` 和 `nodes.py` 文件是否存在
3. 查看ComfyUI的控制台输出是否有错误信息
4. 完全关闭ComfyUI后重新启动（不是刷新网页）

### 问题：导入错误

**解决方案：**
确保ComfyUI本身已正确安装并能正常运行。本节点依赖ComfyUI的基础库。

### 问题：图片输出质量不佳

**解决方案：**
- 确保DPI设置为300或更高
- 使用高分辨率的输入图片
- 检查缩放参数是否合适

### 问题：A4排版图片被截断

**解决方案：**
- 检查页边距设置（margin_mm）
- 确保徽章直径和间距的总和不超过A4尺寸
- 使用"紧凑"模式可以放置更多徽章

## 更新 Updating

### 如果使用Git安装：

```bash
cd ComfyUI/custom_nodes/BadgePatternTool-ComfyUI/
git pull
```

### 如果手动安装：

1. 下载最新版本
2. 删除旧文件夹
3. 解压新版本到相同位置

然后重启ComfyUI。

## 卸载 Uninstalling

```bash
cd ComfyUI/custom_nodes/
rm -rf BadgePatternTool-ComfyUI/
```

或直接删除 `BadgePatternTool-ComfyUI` 文件夹，然后重启ComfyUI。

## 支持 Support

如遇到问题，请：

1. 查看 [README_COMFYUI.md](README_COMFYUI.md) 中的常见问题
2. 查看 [example_workflow.json](example_workflow.json) 中的示例
3. 在GitHub上提交Issue
4. 查看ComfyUI的控制台输出获取详细错误信息

## 系统要求 System Requirements

- ComfyUI (最新版本)
- Python 3.8+
- 足够的内存用于图片处理（建议4GB+）

## 许可证 License

MIT License - 详见LICENSE文件

