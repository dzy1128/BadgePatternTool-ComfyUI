/**
 * BadgePatternTool - 可拖拽编辑器
 * ComfyUI自定义Widget扩展
 */

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// 创建可拖拽编辑器widget
function createDraggableEditor(node, inputName, inputData, app) {
    const widget = {
        type: "badge_draggable_editor",
        name: inputName,
        size: [0, 300],
        
        // 编辑器状态
        state: {
            imageData: null,
            scale: 1.0,
            offsetX: 0,
            offsetY: 0,
            isDragging: false,
            lastMouseX: 0,
            lastMouseY: 0,
            canvasSize: 300
        },

        draw: function(ctx, node, widgetWidth, widgetY, height) {
            const margin = 15;
            const size = widgetWidth - margin * 2;
            const y = widgetY;
            
            // 绘制背景
            ctx.fillStyle = "#1e1e1e";
            ctx.fillRect(margin, y, size, size);
            
            // 绘制边框
            ctx.strokeStyle = "#555";
            ctx.lineWidth = 2;
            ctx.strokeRect(margin, y, size, size);
            
            const centerX = margin + size / 2;
            const centerY = y + size / 2;
            const radius = size * 0.4;
            
            // 绘制圆形边界（红色）
            ctx.strokeStyle = "#ff4444";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();
            
            // 绘制中心十字线（绿色）
            ctx.strokeStyle = "#44ff44";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(centerX - 20, centerY);
            ctx.lineTo(centerX + 20, centerY);
            ctx.moveTo(centerX, centerY - 20);
            ctx.lineTo(centerX, centerY + 20);
            ctx.stroke();
            
            // 如果有图片数据，绘制图片
            if (this.state.imageData) {
                try {
                    ctx.save();
                    
                    // 应用变换
                    const imgX = centerX + this.state.offsetX;
                    const imgY = centerY + this.state.offsetY;
                    
                    ctx.translate(imgX, imgY);
                    ctx.scale(this.state.scale, this.state.scale);
                    
                    // 绘制图片（居中）
                    const imgWidth = this.state.imageData.width;
                    const imgHeight = this.state.imageData.height;
                    ctx.drawImage(this.state.imageData, -imgWidth/2, -imgHeight/2);
                    
                    ctx.restore();
                } catch(e) {
                    console.error("绘制图片失败:", e);
                }
            } else {
                // 绘制提示文本
                ctx.fillStyle = "#888";
                ctx.font = "14px Arial";
                ctx.textAlign = "center";
                ctx.fillText("🖱️ 拖拽移动 | 🔍 滚轮缩放", centerX, centerY);
                ctx.fillText("连接图片输入后显示", centerX, centerY + 20);
            }
            
            // 绘制参数信息
            ctx.fillStyle = "#fff";
            ctx.font = "12px monospace";
            ctx.textAlign = "left";
            ctx.fillText(
                `缩放: ${this.state.scale.toFixed(2)}x | 偏移: (${Math.round(this.state.offsetX)}, ${Math.round(this.state.offsetY)})`,
                margin + 5,
                y + size - 5
            );
            
            // 绘制操作提示
            ctx.fillStyle = "#666";
            ctx.font = "11px Arial";
            ctx.textAlign = "center";
            ctx.fillText("拖拽图片 | 滚轮缩放 | R重置", centerX, y + size + 15);
        },

        mouse: function(event, pos, node) {
            // 获取widget的位置和大小
            const margin = 15;
            const widgetWidth = node.size[0];
            const size = widgetWidth - margin * 2;
            const widgetY = this.last_y || 0;
            
            // 检查鼠标是否在widget区域内
            const relX = pos[0] - margin;
            const relY = pos[1] - widgetY;
            
            if (relX < 0 || relX > size || relY < 0 || relY > size) {
                return false;
            }
            
            if (event.type === "pointerdown") {
                this.state.isDragging = true;
                this.state.lastMouseX = pos[0];
                this.state.lastMouseY = pos[1];
                return true;
            }
            else if (event.type === "pointermove" && this.state.isDragging) {
                const dx = pos[0] - this.state.lastMouseX;
                const dy = pos[1] - this.state.lastMouseY;
                
                this.state.offsetX += dx;
                this.state.offsetY += dy;
                
                this.state.lastMouseX = pos[0];
                this.state.lastMouseY = pos[1];
                
                // 更新节点参数
                this.updateNodeParams();
                
                node.setDirtyCanvas(true, true);
                return true;
            }
            else if (event.type === "pointerup") {
                this.state.isDragging = false;
                return true;
            }
            else if (event.type === "wheel") {
                event.preventDefault();
                
                const delta = event.deltaY > 0 ? 0.9 : 1.1;
                this.state.scale = Math.max(0.1, Math.min(5.0, this.state.scale * delta));
                
                // 更新节点参数
                this.updateNodeParams();
                
                node.setDirtyCanvas(true, true);
                return true;
            }
            else if (event.type === "keydown" && event.key === "r") {
                // R键重置
                this.state.scale = 1.0;
                this.state.offsetX = 0;
                this.state.offsetY = 0;
                this.updateNodeParams();
                node.setDirtyCanvas(true, true);
                return true;
            }
            
            return false;
        },

        updateNodeParams: function() {
            // 找到对应的参数widget并更新
            const node = this.options?.node || app.graph._nodes.find(n => 
                n.widgets?.some(w => w === this)
            );
            
            if (node) {
                const scaleWidget = node.widgets.find(w => w.name === "scale");
                const offsetXWidget = node.widgets.find(w => w.name === "offset_x");
                const offsetYWidget = node.widgets.find(w => w.name === "offset_y");
                
                if (scaleWidget) scaleWidget.value = parseFloat(this.state.scale.toFixed(2));
                if (offsetXWidget) offsetXWidget.value = Math.round(this.state.offsetX);
                if (offsetYWidget) offsetYWidget.value = Math.round(this.state.offsetY);
            }
        },

        computeSize: function(width) {
            return [width, 320];
        }
    };
    
    widget.options = { serialize: false };
    node.addCustomWidget(widget);
    
    return widget;
}

// 注册扩展
app.registerExtension({
    name: "BadgePatternTool.DraggableEditor",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "DraggableEditorNode") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // 创建可拖拽编辑器widget
                const editorWidget = createDraggableEditor(this, "editor", {}, app);
                
                // 监听输入连接变化
                const originalOnConnectionsChange = this.onConnectionsChange;
                this.onConnectionsChange = function(type, index, connected, link_info) {
                    if (originalOnConnectionsChange) {
                        originalOnConnectionsChange.apply(this, arguments);
                    }
                    
                    // 如果是输入连接且已连接
                    if (type === 1 && index === 0 && connected) {
                        // 尝试加载图片预览
                        setTimeout(() => {
                            this.loadImagePreview();
                        }, 100);
                    }
                };
                
                // 加载图片预览的方法
                this.loadImagePreview = async function() {
                    if (!this.inputs?.[0]?.link) return;
                    
                    try {
                        const link = app.graph.links[this.inputs[0].link];
                        if (!link) return;
                        
                        const originNode = app.graph.getNodeById(link.origin_id);
                        if (!originNode) return;
                        
                        // 尝试获取图片数据
                        // 注意：这里可能需要根据实际情况调整
                        if (originNode.imgs && originNode.imgs.length > 0) {
                            const img = new Image();
                            img.crossOrigin = "anonymous";
                            img.onload = () => {
                                if (editorWidget && editorWidget.state) {
                                    editorWidget.state.imageData = img;
                                    this.setDirtyCanvas(true, true);
                                }
                            };
                            img.src = originNode.imgs[0].src;
                        }
                    } catch(e) {
                        console.error("加载图片预览失败:", e);
                    }
                };
                
                return result;
            };
        }
    }
});

console.log("✅ BadgePatternTool 可拖拽编辑器已加载");

