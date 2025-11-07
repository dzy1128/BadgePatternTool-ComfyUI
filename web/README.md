# Web 前端文件说明

## 文件列表

- `badge_interactive.js` - 交互式拖拽编辑器的前端实现

## 功能说明

这个前端扩展为ComfyUI添加了交互式GUI功能，允许用户：

- 🖱️ 用鼠标拖拽图片位置
- 🔍 用滚轮缩放图片大小
- 👁️ 实时查看裁剪边界和参考线

## 技术实现

### 注册自定义Widget

```javascript
app.registerExtension({
    name: "BadgePatternTool.InteractiveEditor",
    // ...
});
```

### 自定义绘制

在`draw`函数中实现：
- Canvas绘制
- 图片渲染
- 参考线显示

### 鼠标事件处理

在`mouse`函数中实现：
- mousedown: 开始拖拽
- mousemove: 拖拽移动
- mouseup: 结束拖拽
- wheel: 缩放处理

## 修改指南

### 调整画布大小

修改 `computeSize` 函数：

```javascript
computeSize: function(width) {
    return [width, 300];  // 第二个参数是高度
}
```

### 调整缩放灵敏度

修改 wheel 事件中的 delta 值：

```javascript
const delta = event.deltaY > 0 ? 0.95 : 1.05;
// 改为: 0.98 和 1.02 会更平滑
```

### 调整参考线颜色

修改 draw 函数中的颜色值：

```javascript
ctx.strokeStyle = "rgba(255, 0, 0, 0.8)";  // 红色圆圈
ctx.strokeStyle = "rgba(0, 255, 0, 0.5)";  // 绿色十字
```

## 调试

### 浏览器控制台

按F12打开开发者工具，应该看到：

```
BadgePatternTool 交互式编辑器已加载
```

### 常见问题

1. **JS未加载**: 检查文件路径是否正确
2. **功能不生效**: 清空浏览器缓存后刷新
3. **渲染错误**: 查看控制台错误信息

## 兼容性

- **ComfyUI版本**: 需要支持自定义前端扩展的版本
- **浏览器**: Chrome/Edge/Firefox 现代版本
- **Canvas API**: 必需

## 许可证

MIT License - 与主项目保持一致

