# 快速开始 - Quick Start

## ⚡ 5分钟上手指南

### 步骤1：安装（30秒）

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/BadgePatternTool-ComfyUI.git
```

重启ComfyUI即可！

### 步骤2：找到节点（10秒）

在ComfyUI中右键点击画布，查找 **"徽章工具"** 分类：

- 🔵 圆形徽章裁剪
- 🟢 徽章A4排版  
- 🟡 自动优化徽章参数

### 步骤3：创建第一个工作流（2分钟）

#### 方案A：单张徽章制作

```
1. 添加 [Load Image] 节点，加载图片
2. 添加 [圆形徽章裁剪] 节点
3. 连接：Load Image → 圆形徽章裁剪
4. 设置参数：
   - diameter_mm: 58
   - dpi: 300
5. 添加 [Save Image] 保存结果
6. 点击执行 ▶️
```

#### 方案B：批量A4排版（推荐）

```
1. 添加 [Load Image] 节点（可选择多张图片）
2. 添加 [圆形徽章裁剪] 节点
3. 添加 [徽章A4排版] 节点
4. 连接：Load Image → 圆形徽章裁剪 → 徽章A4排版
5. 设置参数：
   徽章A4排版：
   - layout_type: 紧凑
   - spacing_mm: 5
   - margin_mm: 10
6. 添加 [Save Image]
7. 点击执行 ▶️
```

### 步骤4：保存和打印（1分钟）

1. 从ComfyUI输出文件夹找到生成的图片
2. 使用A4纸打印（推荐设置：300 DPI，彩色）
3. 按照圆形边缘裁剪
4. 完成！🎉

---

## 🎯 常用参数速查

### 标准58mm徽章
```
diameter_mm: 58.0
scale: 1.0
dpi: 300
spacing_mm: 5.0
margin_mm: 10.0
layout_type: "紧凑"
```

**预期结果**: A4纸上约15-18个徽章

### 小型32mm徽章
```
diameter_mm: 32.0
spacing_mm: 3.0
layout_type: "网格"
```

**预期结果**: A4纸上约30-35个徽章

---

## 💡 3个实用技巧

### 技巧1：使用自动优化

不知道设置多少缩放？试试自动优化节点：

```
Load Image → 自动优化徽章参数 → 圆形徽章裁剪
                ↓                    ↑
                └──（连接scale参数）──┘
```

### 技巧2：批次处理

在Load Image节点中选择多张图片，它们会自动作为批次处理，无需重复创建节点！

### 技巧3：预览中间结果

在任何节点后面添加 [Preview Image] 节点查看中间结果，帮助调试参数。

---

## 🆘 遇到问题？

### 问题1：节点找不到
**解决**: 
1. 确认文件夹名是 `BadgePatternTool-ComfyUI`
2. 完全关闭并重启ComfyUI（不是刷新）
3. 查看控制台是否有错误

### 问题2：图片被裁掉了
**解决**: 
- 增大 `scale` 参数（如1.5）
- 或使用"自动优化"节点

### 问题3：排版图空白
**解决**: 
- 确保输入的是批次图片
- 检查徽章直径不要太大
- 尝试减小margin_mm

---

## 📚 更多资源

- **详细教程**: [README_COMFYUI.md](README_COMFYUI.md)
- **安装指南**: [INSTALL.md](INSTALL.md)
- **测试方法**: [TESTING.md](TESTING.md)
- **工作流示例**: [example_workflow.json](example_workflow.json)

---

## 🎨 推荐工作流

### 初学者推荐
```
Load Image → 圆形徽章裁剪 → Preview Image
```
先熟悉单个节点的效果

### 日常使用推荐
```
Load Image (批次) → 圆形徽章裁剪 → 徽章A4排版 → Save Image
```
最常用的批量制作流程

### 专业用户推荐
```
Load Image → 自动优化 → 圆形裁剪 → 调整参数 → A4排版 → Save Image
```
完整的工作流，精确控制每个环节

---

## ✅ 检查清单

准备好了吗？确认以下事项：

- [ ] ComfyUI正常运行
- [ ] 节点已正确安装
- [ ] 可以在节点菜单中找到"徽章工具"分类
- [ ] 准备好要制作的图片（建议≥1000x1000px）
- [ ] 了解基本参数的含义

**全部勾选？开始创作吧！** 🚀

---

**祝您使用愉快！如有问题，欢迎提Issue反馈。**

