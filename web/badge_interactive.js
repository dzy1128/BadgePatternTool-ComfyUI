/**
 * BadgePatternTool - ComfyUI 交互式前端扩展
 * 实现可拖拽、缩放的交互式图片编辑器
 */

import { app } from "../../scripts/app.js";

// 注册交互式编辑器组件
app.registerExtension({
    name: "BadgePatternTool.InteractiveEditor",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 只对我们的交互式节点添加扩展
        if (nodeData.name === "InteractiveImageEditorNode") {
            // 保存原始的onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // 添加编辑器画布widget
                const editorWidget = this.addCustomWidget({
                    name: "interactive_editor",
                    type: "badge_editor",
                    value: {
                        scale: 1.0,
                        offsetX: 0,
                        offsetY: 0,
                        dragging: false,
                        lastMouseX: 0,
                        lastMouseY: 0
                    },
                    options: {},
                    draw: function(ctx, node, width, y) {
                        // 绘制画布背景
                        ctx.fillStyle = "#2a2a2a";
                        ctx.fillRect(0, y, width, 300);
                        
                        // 绘制边框
                        ctx.strokeStyle = "#4a4a4a";
                        ctx.lineWidth = 2;
                        ctx.strokeRect(0, y, width, 300);
                        
                        // 绘制提示文本
                        ctx.fillStyle = "#888";
                        ctx.font = "14px Arial";
                        ctx.textAlign = "center";
                        ctx.fillText("🖱️ 拖拽移动 | 🔍 滚轮缩放", width / 2, y + 150);
                        
                        // 如果有图片，绘制图片预览
                        if (this.imageElement) {
                            try {
                                const centerX = width / 2;
                                const centerY = y + 150;
                                
                                // 应用变换
                                ctx.save();
                                ctx.translate(centerX + this.value.offsetX, centerY + this.value.offsetY);
                                ctx.scale(this.value.scale, this.value.scale);
                                
                                // 绘制图片（居中）
                                const imgW = this.imageElement.width;
                                const imgH = this.imageElement.height;
                                ctx.drawImage(this.imageElement, -imgW/2, -imgH/2, imgW, imgH);
                                
                                ctx.restore();
                                
                                // 绘制圆形边界参考线
                                const diameter = node.widgets.find(w => w.name === "diameter_mm")?.value || 58;
                                const dpi = node.widgets.find(w => w.name === "dpi")?.value || 300;
                                const radius = (diameter / 25.4 * dpi) / 2 * 0.5; // 缩小到适合画布
                                
                                ctx.strokeStyle = "rgba(255, 0, 0, 0.8)";
                                ctx.lineWidth = 2;
                                ctx.beginPath();
                                ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                                ctx.stroke();
                                
                                // 绘制十字参考线
                                ctx.strokeStyle = "rgba(0, 255, 0, 0.5)";
                                ctx.lineWidth = 1;
                                ctx.beginPath();
                                ctx.moveTo(centerX - 50, centerY);
                                ctx.lineTo(centerX + 50, centerY);
                                ctx.moveTo(centerX, centerY - 50);
                                ctx.lineTo(centerX, centerY + 50);
                                ctx.stroke();
                                
                            } catch (e) {
                                console.error("绘制图片失败:", e);
                            }
                        }
                        
                        // 显示当前参数
                        ctx.fillStyle = "#fff";
                        ctx.font = "12px monospace";
                        ctx.textAlign = "left";
                        ctx.fillText(
                            `缩放: ${this.value.scale.toFixed(2)}x | 偏移: (${this.value.offsetX}, ${this.value.offsetY})`,
                            10, y + 290
                        );
                    },
                    mouse: function(event, pos, node) {
                        const widgetY = this.last_y || 0;
                        const relY = pos[1] - widgetY;
                        
                        // 检查鼠标是否在widget区域内
                        if (relY < 0 || relY > 300) return false;
                        
                        const canvas = app.canvas;
                        const scale = canvas.ds.scale;
                        
                        if (event.type === "mousedown") {
                            this.value.dragging = true;
                            this.value.lastMouseX = pos[0];
                            this.value.lastMouseY = pos[1];
                            return true;
                        }
                        else if (event.type === "mousemove" && this.value.dragging) {
                            const dx = (pos[0] - this.value.lastMouseX) / scale;
                            const dy = (pos[1] - this.value.lastMouseY) / scale;
                            
                            this.value.offsetX += dx;
                            this.value.offsetY += dy;
                            
                            this.value.lastMouseX = pos[0];
                            this.value.lastMouseY = pos[1];
                            
                            // 更新节点的offset参数
                            const offsetXWidget = node.widgets.find(w => w.name === "offset_x");
                            const offsetYWidget = node.widgets.find(w => w.name === "offset_y");
                            if (offsetXWidget) offsetXWidget.value = Math.round(this.value.offsetX);
                            if (offsetYWidget) offsetYWidget.value = Math.round(this.value.offsetY);
                            
                            node.setDirtyCanvas(true);
                            return true;
                        }
                        else if (event.type === "mouseup") {
                            this.value.dragging = false;
                            return true;
                        }
                        else if (event.type === "wheel") {
                            event.preventDefault();
                            
                            const delta = event.deltaY > 0 ? 0.95 : 1.05;
                            this.value.scale = Math.max(0.1, Math.min(5.0, this.value.scale * delta));
                            
                            // 更新节点的scale参数
                            const scaleWidget = node.widgets.find(w => w.name === "scale");
                            if (scaleWidget) {
                                scaleWidget.value = parseFloat(this.value.scale.toFixed(2));
                            }
                            
                            node.setDirtyCanvas(true);
                            return true;
                        }
                        
                        return false;
                    },
                    computeSize: function(width) {
                        return [width, 300];
                    }
                });
                
                // 监听图片输入变化
                this.onConnectionsChange = function(type, index, connected, link_info) {
                    if (type === 1 && index === 0 && connected) { // 输入连接
                        // 尝试获取输入图片
                        setTimeout(() => {
                            this.updateEditorImage();
                        }, 100);
                    }
                };
                
                // 添加更新图片的方法
                this.updateEditorImage = function() {
                    if (this.inputs?.[0]?.link != null) {
                        const link = app.graph.links[this.inputs[0].link];
                        if (link) {
                            const originNode = app.graph.getNodeById(link.origin_id);
                            // 这里可以尝试获取图片，但ComfyUI的图片数据不容易直接访问
                            // 暂时显示占位符
                        }
                    }
                };
                
                return result;
            };
        }
    }
});

console.log("BadgePatternTool 交互式编辑器已加载");

