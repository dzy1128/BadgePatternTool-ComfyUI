"""
ComfyUI节点 - 徽章图案工具
Badge Pattern Tool Nodes for ComfyUI
"""

import torch
import numpy as np
from PIL import Image, ImageDraw
import math


def tensor2pil(image):
    """将ComfyUI的tensor图片转换为PIL Image"""
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


def pil2tensor(image):
    """将PIL Image转换为ComfyUI的tensor格式"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


class CircularCropNode:
    """圆形裁剪节点 - 将图片裁剪成圆形徽章"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0,
                    "display": "number"
                }),
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "rotation": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 360,
                    "step": 1
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("圆形徽章",)
    FUNCTION = "crop_to_circle"
    CATEGORY = "徽章工具"
    
    def crop_to_circle(self, image, diameter_mm, scale, offset_x, offset_y, rotation, dpi):
        """
        将图片裁剪成圆形徽章
        
        参数:
            image: 输入图片（tensor格式）
            diameter_mm: 徽章直径（毫米）
            scale: 缩放比例
            offset_x: X轴偏移（像素）
            offset_y: Y轴偏移（像素）
            rotation: 旋转角度（度）
            dpi: 分辨率（每英寸点数）
        """
        # 转换为PIL图片
        pil_image = tensor2pil(image)
        
        # 计算圆形直径（像素）
        circle_diameter_px = int(diameter_mm / 25.4 * dpi)
        circle_radius_px = circle_diameter_px // 2
        
        # 转换为RGB模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 应用旋转
        if rotation != 0:
            pil_image = pil_image.rotate(rotation, expand=True, fillcolor=(255, 255, 255))
        
        # 应用缩放
        if scale != 1.0:
            orig_width, orig_height = pil_image.size
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建圆形裁剪
        circle_img = self._crop_to_circle(pil_image, circle_diameter_px, offset_x, offset_y)
        
        # 转换回tensor
        return (pil2tensor(circle_img),)
    
    def _crop_to_circle(self, img, circle_size, offset_x=0, offset_y=0):
        """
        将图片裁剪为圆形
        
        参数:
            img: PIL Image对象
            circle_size: 圆形直径（像素）
            offset_x: X轴偏移
            offset_y: Y轴偏移
        """
        img_width, img_height = img.size
        
        # 计算粘贴位置
        center_x = circle_size // 2
        center_y = circle_size // 2
        paste_x = center_x - img_width // 2 + offset_x
        paste_y = center_y - img_height // 2 + offset_y
        
        # 创建RGBA图像
        circle_img = Image.new('RGBA', (circle_size, circle_size), (255, 255, 255, 0))
        
        # 创建白色背景并粘贴图片
        temp_canvas = Image.new('RGB', (circle_size, circle_size), (255, 255, 255))
        temp_canvas.paste(img, (paste_x, paste_y))
        
        # 创建圆形遮罩
        mask = Image.new('L', (circle_size, circle_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, circle_size, circle_size], fill=255)
        
        # 应用遮罩
        circle_img.paste(temp_canvas, (0, 0))
        circle_img.putalpha(mask)
        
        # 转换为RGB（去除透明通道，用白色背景）
        final_img = Image.new('RGB', (circle_size, circle_size), (255, 255, 255))
        final_img.paste(circle_img, (0, 0), circle_img)
        
        return final_img


class BadgeLayoutNode:
    """徽章排版节点 - 在A4纸上智能排版多个圆形徽章"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0
                }),
                "layout_type": (["网格", "紧凑"],),
                "spacing_mm": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.0,
                    "max": 20.0,
                    "step": 0.5
                }),
                "margin_mm": ("FLOAT", {
                    "default": 10.0,
                    "min": 0.0,
                    "max": 50.0,
                    "step": 1.0
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("A4排版图",)
    FUNCTION = "create_layout"
    CATEGORY = "徽章工具"
    
    def create_layout(self, images, diameter_mm, layout_type, spacing_mm, margin_mm, dpi):
        """
        在A4纸上排版圆形徽章
        
        参数:
            images: 输入图片列表（tensor格式，可以是批次）
            diameter_mm: 徽章直径（毫米）
            layout_type: 排版类型（网格/紧凑）
            spacing_mm: 间距（毫米）
            margin_mm: 页边距（毫米）
            dpi: 分辨率
        """
        # A4纸尺寸（像素）
        a4_width_px = int(210 / 25.4 * dpi)
        a4_height_px = int(297 / 25.4 * dpi)
        
        # 计算徽章尺寸（像素）
        badge_diameter_px = int(diameter_mm / 25.4 * dpi)
        badge_radius_px = badge_diameter_px // 2
        spacing_px = int(spacing_mm / 25.4 * dpi)
        margin_px = int(margin_mm / 25.4 * dpi)
        
        # 计算布局
        if layout_type == "网格":
            layout = self._calculate_grid_layout(
                a4_width_px, a4_height_px, badge_diameter_px, 
                badge_radius_px, spacing_px, margin_px
            )
        else:
            layout = self._calculate_compact_layout(
                a4_width_px, a4_height_px, badge_diameter_px, 
                badge_radius_px, spacing_px, margin_px
            )
        
        # 创建A4画布
        canvas = Image.new('RGB', (a4_width_px, a4_height_px), (255, 255, 255))
        
        # 绘制页边距线（辅助线）
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([
            margin_px, margin_px,
            a4_width_px - margin_px, a4_height_px - margin_px
        ], outline=(200, 200, 200), width=2)
        
        # 放置图片
        positions = layout['positions']
        batch_size = images.shape[0] if len(images.shape) == 4 else 1
        
        for i in range(min(batch_size, len(positions))):
            # 获取单张图片
            if len(images.shape) == 4:
                single_image = images[i]
            else:
                single_image = images
            
            # 转换为PIL
            pil_img = tensor2pil(single_image)
            
            # 确保是圆形（如果不是，进行裁剪）
            if pil_img.size != (badge_diameter_px, badge_diameter_px):
                pil_img = pil_img.resize((badge_diameter_px, badge_diameter_px), Image.Resampling.LANCZOS)
            
            # 获取位置
            center_x, center_y = positions[i]
            paste_x = center_x - badge_radius_px
            paste_y = center_y - badge_radius_px
            
            # 粘贴到画布
            canvas.paste(pil_img, (paste_x, paste_y))
        
        # 在剩余位置绘制占位符
        for i in range(batch_size, len(positions)):
            center_x, center_y = positions[i]
            draw.ellipse([
                center_x - badge_radius_px, center_y - badge_radius_px,
                center_x + badge_radius_px, center_y + badge_radius_px
            ], fill=(220, 220, 220), outline=(200, 200, 200), width=1)
        
        # 转换回tensor
        return (pil2tensor(canvas),)
    
    def _calculate_grid_layout(self, a4_width, a4_height, diameter, radius, spacing, margin):
        """计算网格排列布局"""
        available_width = a4_width - 2 * margin
        available_height = a4_height - 2 * margin
        
        # 圆心之间的距离
        center_distance = diameter + spacing
        
        # 计算每行和每列可放置的圆形数量
        cols = max(1, int(available_width // center_distance))
        rows = max(1, int(available_height // center_distance))
        
        # 计算起始位置（居中）
        total_width = cols * center_distance
        total_height = rows * center_distance
        start_x = margin + (available_width - total_width) / 2
        start_y = margin + (available_height - total_height) / 2
        
        # 生成位置列表
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * center_distance + radius
                y = start_y + row * center_distance + radius
                positions.append((int(x), int(y)))
        
        return {
            'type': 'grid',
            'positions': positions,
            'rows': rows,
            'cols': cols,
            'max_count': rows * cols
        }
    
    def _calculate_compact_layout(self, a4_width, a4_height, diameter, radius, spacing, margin):
        """计算紧凑排列布局（六边形蜂巢）"""
        available_width = a4_width - 2 * margin
        available_height = a4_height - 2 * margin
        
        # 圆心之间的最小距离
        min_center_distance = diameter + spacing
        
        # 六边形网格的水平间距
        hex_horizontal_factor = math.sqrt(3) / 2
        horizontal_spacing = diameter * hex_horizontal_factor + spacing
        
        # 计算列数
        max_cols = max(1, int((available_width + horizontal_spacing) // horizontal_spacing))
        
        # 垂直间距
        vertical_spacing = max(horizontal_spacing * math.sqrt(3) / 2, min_center_distance)
        middle_col_offset = vertical_spacing / 2
        
        # 起始位置
        start_x = margin + radius
        
        # 生成位置列表
        positions = []
        for col in range(max_cols):
            # 计算列的X位置
            x = start_x + col * horizontal_spacing
            
            # 边界检查
            if x - radius < margin or x + radius > a4_width - margin:
                continue
            
            # 计算当前列的Y起始位置
            if col % 2 == 0:  # 偶数列
                y_start = margin + radius
            else:  # 奇数列 - 向下偏移
                y_start = margin + radius + middle_col_offset
            
            # 在当前列中放置圆形
            y = y_start
            while y + radius <= a4_height - margin:
                positions.append((int(x), int(y)))
                y += vertical_spacing
        
        return {
            'type': 'compact',
            'positions': positions,
            'max_count': len(positions)
        }


class AutoOptimizeBadgeNode:
    """自动优化徽章参数节点 - 自动计算最佳缩放和位置"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("FLOAT", "INT", "INT")
    RETURN_NAMES = ("最佳缩放", "偏移X", "偏移Y")
    FUNCTION = "optimize"
    CATEGORY = "徽章工具"
    
    def optimize(self, image, diameter_mm, dpi):
        """
        自动计算最佳参数
        
        返回最佳的缩放比例和偏移量，使图片完美填充圆形
        """
        # 转换为PIL
        pil_image = tensor2pil(image)
        
        # 计算圆形直径（像素）
        circle_diameter_px = int(diameter_mm / 25.4 * dpi)
        
        # 获取图片尺寸
        img_width, img_height = pil_image.size
        
        # 计算最佳缩放比例（使图片刚好填满圆形）
        scale_x = circle_diameter_px / img_width
        scale_y = circle_diameter_px / img_height
        optimal_scale = max(scale_x, scale_y)
        
        # 偏移为0（居中）
        offset_x = 0
        offset_y = 0
        
        return (optimal_scale, offset_x, offset_y)


class InteractivePreviewNode:
    """交互式预览节点 - 生成带有参考线和网格的预览图，帮助调整参数"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0
                }),
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01
                }),
                "offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
                "show_grid": (["是", "否"],),
                "show_safe_area": (["是", "否"],),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("预览图", "参数提示")
    FUNCTION = "create_preview"
    CATEGORY = "徽章工具/交互辅助"
    
    def create_preview(self, image, diameter_mm, scale, offset_x, offset_y, dpi, show_grid, show_safe_area):
        """
        创建交互式预览图
        显示当前裁剪效果、参考线、网格等，帮助用户调整参数
        """
        # 转换为PIL
        pil_image = tensor2pil(image)
        
        # 计算圆形直径
        circle_diameter_px = int(diameter_mm / 25.4 * dpi)
        circle_radius_px = circle_diameter_px // 2
        
        # 应用缩放
        if scale != 1.0:
            orig_width, orig_height = pil_image.size
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建预览画布（比圆形大一些，方便观察）
        preview_size = int(circle_diameter_px * 1.5)
        preview_canvas = Image.new('RGB', (preview_size, preview_size), (240, 240, 240))
        draw = ImageDraw.Draw(preview_canvas)
        
        # 计算图片粘贴位置
        canvas_center_x = preview_size // 2
        canvas_center_y = preview_size // 2
        img_width, img_height = pil_image.size
        paste_x = canvas_center_x - img_width // 2 + offset_x
        paste_y = canvas_center_y - img_height // 2 + offset_y
        
        # 粘贴图片
        preview_canvas.paste(pil_image, (paste_x, paste_y))
        
        # 绘制圆形边界（红色）
        circle_left = canvas_center_x - circle_radius_px
        circle_top = canvas_center_y - circle_radius_px
        circle_right = canvas_center_x + circle_radius_px
        circle_bottom = canvas_center_y + circle_radius_px
        draw.ellipse([circle_left, circle_top, circle_right, circle_bottom], 
                     outline=(255, 0, 0), width=3)
        
        # 绘制安全区域（蓝色虚线）
        if show_safe_area == "是":
            safe_radius = int(circle_radius_px * 0.9)
            safe_left = canvas_center_x - safe_radius
            safe_top = canvas_center_y - safe_radius
            safe_right = canvas_center_x + safe_radius
            safe_bottom = canvas_center_y + safe_radius
            # 绘制虚线圆
            for angle in range(0, 360, 10):
                rad1 = math.radians(angle)
                rad2 = math.radians(angle + 5)
                x1 = canvas_center_x + int(safe_radius * math.cos(rad1))
                y1 = canvas_center_y + int(safe_radius * math.sin(rad1))
                x2 = canvas_center_x + int(safe_radius * math.cos(rad2))
                y2 = canvas_center_y + int(safe_radius * math.sin(rad2))
                draw.line([x1, y1, x2, y2], fill=(0, 0, 255), width=2)
        
        # 绘制十字参考线（绿色）
        draw.line([0, canvas_center_y, preview_size, canvas_center_y], 
                  fill=(0, 255, 0), width=1)
        draw.line([canvas_center_x, 0, canvas_center_x, preview_size], 
                  fill=(0, 255, 0), width=1)
        
        # 绘制网格
        if show_grid == "是":
            grid_spacing = circle_radius_px // 4
            for i in range(-preview_size, preview_size, grid_spacing):
                # 竖线
                draw.line([canvas_center_x + i, 0, canvas_center_x + i, preview_size], 
                         fill=(200, 200, 200), width=1)
                # 横线
                draw.line([0, canvas_center_y + i, preview_size, canvas_center_y + i], 
                         fill=(200, 200, 200), width=1)
        
        # 生成参数提示文本
        hint_text = f"""当前参数:
缩放: {scale:.2f}x
偏移X: {offset_x}px (负值←左, 正值→右)
偏移Y: {offset_y}px (负值↑上, 正值↓下)
徽章直径: {diameter_mm}mm ({circle_diameter_px}px)

调整建议:
- 图片太小/太大: 调整scale参数
- 位置偏左: 增大offset_x (向右移)
- 位置偏右: 减小offset_x (向左移)
- 位置偏上: 增大offset_y (向下移)
- 位置偏下: 减小offset_y (向上移)

参考线说明:
🔴 红圈: 最终裁剪边界
🔵 蓝圈: 安全区域(建议主体在此内)
🟢 十字: 中心参考线
⬜ 网格: 位置参考"""
        
        # 转换回tensor
        return (pil2tensor(preview_canvas), hint_text)


class ParameterAdjustNode:
    """参数微调节点 - 提供便捷的增量调整"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "current_scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01
                }),
                "current_offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "current_offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "adjust_scale": (["不变", "放大10%", "放大5%", "缩小5%", "缩小10%", "重置为1.0"],),
                "adjust_x": (["不变", "左移50", "左移10", "右移10", "右移50", "重置为0"],),
                "adjust_y": (["不变", "上移50", "上移10", "下移10", "下移50", "重置为0"],),
            },
        }
    
    RETURN_TYPES = ("FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("新缩放", "新偏移X", "新偏移Y", "变化说明")
    FUNCTION = "adjust_parameters"
    CATEGORY = "徽章工具/交互辅助"
    
    def adjust_parameters(self, current_scale, current_offset_x, current_offset_y, 
                         adjust_scale, adjust_x, adjust_y):
        """
        根据选择的调整选项，计算新的参数值
        """
        new_scale = current_scale
        new_x = current_offset_x
        new_y = current_offset_y
        changes = []
        
        # 调整缩放
        if adjust_scale == "放大10%":
            new_scale = min(5.0, current_scale * 1.1)
            changes.append(f"缩放: {current_scale:.2f} → {new_scale:.2f} (放大10%)")
        elif adjust_scale == "放大5%":
            new_scale = min(5.0, current_scale * 1.05)
            changes.append(f"缩放: {current_scale:.2f} → {new_scale:.2f} (放大5%)")
        elif adjust_scale == "缩小5%":
            new_scale = max(0.1, current_scale * 0.95)
            changes.append(f"缩放: {current_scale:.2f} → {new_scale:.2f} (缩小5%)")
        elif adjust_scale == "缩小10%":
            new_scale = max(0.1, current_scale * 0.9)
            changes.append(f"缩放: {current_scale:.2f} → {new_scale:.2f} (缩小10%)")
        elif adjust_scale == "重置为1.0":
            new_scale = 1.0
            changes.append(f"缩放: {current_scale:.2f} → 1.0 (重置)")
        
        # 调整X偏移
        if adjust_x == "左移50":
            new_x = max(-1000, current_offset_x - 50)
            changes.append(f"X偏移: {current_offset_x} → {new_x} (左移50px)")
        elif adjust_x == "左移10":
            new_x = max(-1000, current_offset_x - 10)
            changes.append(f"X偏移: {current_offset_x} → {new_x} (左移10px)")
        elif adjust_x == "右移10":
            new_x = min(1000, current_offset_x + 10)
            changes.append(f"X偏移: {current_offset_x} → {new_x} (右移10px)")
        elif adjust_x == "右移50":
            new_x = min(1000, current_offset_x + 50)
            changes.append(f"X偏移: {current_offset_x} → {new_x} (右移50px)")
        elif adjust_x == "重置为0":
            new_x = 0
            changes.append(f"X偏移: {current_offset_x} → 0 (重置)")
        
        # 调整Y偏移
        if adjust_y == "上移50":
            new_y = max(-1000, current_offset_y - 50)
            changes.append(f"Y偏移: {current_offset_y} → {new_y} (上移50px)")
        elif adjust_y == "上移10":
            new_y = max(-1000, current_offset_y - 10)
            changes.append(f"Y偏移: {current_offset_y} → {new_y} (上移10px)")
        elif adjust_y == "下移10":
            new_y = min(1000, current_offset_y + 10)
            changes.append(f"Y偏移: {current_offset_y} → {new_y} (下移10px)")
        elif adjust_y == "下移50":
            new_y = min(1000, current_offset_y + 50)
            changes.append(f"Y偏移: {current_offset_y} → {new_y} (下移50px)")
        elif adjust_y == "重置为0":
            new_y = 0
            changes.append(f"Y偏移: {current_offset_y} → 0 (重置)")
        
        # 生成变化说明
        if changes:
            change_text = "参数调整:\n" + "\n".join(changes)
        else:
            change_text = "参数未变化"
        
        return (new_scale, new_x, new_y, change_text)


class VisualGuideCropNode:
    """可视化引导裁剪节点 - 结合预览和裁剪的一体化节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0
                }),
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("裁剪结果", "预览图", "参数信息")
    FUNCTION = "process"
    CATEGORY = "徽章工具/交互辅助"
    
    def process(self, image, diameter_mm, scale, offset_x, offset_y, dpi):
        """
        同时输出裁剪结果和带参考线的预览图
        方便在一个节点中查看效果并调整
        """
        # 1. 生成裁剪结果
        crop_node = CircularCropNode()
        cropped = crop_node.crop_to_circle(image, diameter_mm, scale, offset_x, offset_y, 0, dpi)
        
        # 2. 生成预览图
        preview_node = InteractivePreviewNode()
        preview, hint = preview_node.create_preview(
            image, diameter_mm, scale, offset_x, offset_y, dpi, "是", "是"
        )
        
        # 3. 生成参数信息
        circle_diameter_px = int(diameter_mm / 25.4 * dpi)
        info = f"""参数总览:
徽章直径: {diameter_mm}mm ({circle_diameter_px}px @ {dpi}dpi)
缩放比例: {scale:.2f}x
X轴偏移: {offset_x}px
Y轴偏移: {offset_y}px

快速调整提示:
1. 观察预览图中的红圈(裁剪边界)
2. 确保主体内容在蓝圈(安全区)内
3. 使用参数微调节点快速调整
4. 或直接修改上方的scale/offset参数"""
        
        return (cropped[0], preview[0], info)


class InteractiveImageEditorNode:
    """
    交互式图片编辑器节点 - 支持鼠标拖拽和滚轮缩放
    
    注意：此节点需要前端JavaScript支持
    前端文件位于: web/badge_interactive.js
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "diameter_mm": ("FLOAT", {
                    "default": 58.0,
                    "min": 10.0,
                    "max": 200.0,
                    "step": 1.0
                }),
                "dpi": ("INT", {
                    "default": 300,
                    "min": 72,
                    "max": 600,
                    "step": 1
                }),
            },
            "optional": {
                "scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01,
                    "display": "number"
                }),
                "offset_x": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
                "offset_y": ("INT", {
                    "default": 0,
                    "min": -1000,
                    "max": 1000,
                    "step": 1
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("裁剪结果", "当前缩放", "当前偏移X", "当前偏移Y", "使用说明")
    FUNCTION = "interactive_edit"
    CATEGORY = "徽章工具/交互编辑"
    
    # 告诉ComfyUI这个节点有自定义widget
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 强制每次都重新计算，保证参数更新
        return float("nan")
    
    def interactive_edit(self, image, diameter_mm, dpi, scale=1.0, offset_x=0, offset_y=0):
        """
        交互式编辑功能
        
        前端会自动更新scale、offset_x、offset_y参数
        用户可以：
        - 鼠标拖拽图片移动位置
        - 滚轮缩放图片大小
        - 实时看到圆形边界参考线
        """
        # 使用当前参数进行裁剪
        crop_node = CircularCropNode()
        result = crop_node.crop_to_circle(
            image=image,
            diameter_mm=diameter_mm,
            scale=scale,
            offset_x=offset_x,
            offset_y=offset_y,
            rotation=0,
            dpi=dpi
        )
        
        # 生成使用说明
        instructions = f"""交互式编辑器使用说明:

🖱️ 鼠标操作:
• 拖拽: 按住鼠标左键拖动图片
• 缩放: 滚动鼠标滚轮放大/缩小

📊 当前参数:
• 缩放: {scale:.2f}x
• X偏移: {offset_x}px
• Y偏移: {offset_y}px
• 徽章直径: {diameter_mm}mm

🔴 红色圆圈 = 裁剪边界
🟢 绿色十字 = 中心参考点

💡 提示:
• 参数会自动同步到节点
• 调整满意后执行工作流
• 可以连接到其他节点继续处理"""
        
        return (result[0], scale, offset_x, offset_y, instructions)


# 节点映射字典
NODE_CLASS_MAPPINGS = {
    "CircularCropNode": CircularCropNode,
    "BadgeLayoutNode": BadgeLayoutNode,
    "AutoOptimizeBadgeNode": AutoOptimizeBadgeNode,
    "InteractivePreviewNode": InteractivePreviewNode,
    "ParameterAdjustNode": ParameterAdjustNode,
    "VisualGuideCropNode": VisualGuideCropNode,
    "InteractiveImageEditorNode": InteractiveImageEditorNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "CircularCropNode": "圆形徽章裁剪",
    "BadgeLayoutNode": "徽章A4排版",
    "AutoOptimizeBadgeNode": "自动优化徽章参数",
    "InteractivePreviewNode": "交互式预览",
    "ParameterAdjustNode": "参数微调",
    "VisualGuideCropNode": "可视化引导裁剪",
    "InteractiveImageEditorNode": "🎮 交互式拖拽编辑器",
}

# Web目录配置（告诉ComfyUI加载前端文件）
WEB_DIRECTORY = "./web"

