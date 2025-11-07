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


# 节点映射字典
NODE_CLASS_MAPPINGS = {
    "CircularCropNode": CircularCropNode,
    "BadgeLayoutNode": BadgeLayoutNode,
    "AutoOptimizeBadgeNode": AutoOptimizeBadgeNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "CircularCropNode": "圆形徽章裁剪",
    "BadgeLayoutNode": "徽章A4排版",
    "AutoOptimizeBadgeNode": "自动优化徽章参数",
}

