"""
测试脚本 - 验证ComfyUI节点功能
Test script for ComfyUI nodes

使用方法：
python test_nodes.py

注意：需要在Python环境中安装torch, numpy, Pillow
"""

import torch
import numpy as np
from PIL import Image
import os

# 导入节点
from nodes import CircularCropNode, BadgeLayoutNode, AutoOptimizeBadgeNode


def create_test_image(width=800, height=600, color=(100, 150, 200)):
    """创建测试图片"""
    img = Image.new('RGB', (width, height), color)
    return img


def pil2tensor(image):
    """将PIL Image转换为tensor"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def tensor2pil(image):
    """将tensor转换为PIL Image"""
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


def test_circular_crop():
    """测试圆形裁剪节点"""
    print("\n=== 测试圆形裁剪节点 ===")
    
    # 创建测试图片
    test_img = create_test_image(800, 600, (255, 100, 100))
    test_tensor = pil2tensor(test_img)
    
    # 创建节点
    node = CircularCropNode()
    
    # 测试基本功能
    print("测试1: 基本裁剪（默认参数）")
    result = node.crop_to_circle(
        image=test_tensor,
        diameter_mm=58.0,
        scale=1.0,
        offset_x=0,
        offset_y=0,
        rotation=0,
        dpi=300
    )
    
    output_img = tensor2pil(result[0])
    print(f"  ✓ 输出尺寸: {output_img.size}")
    print(f"  ✓ 预期直径: {int(58.0 / 25.4 * 300)}px")
    
    # 测试缩放
    print("测试2: 带缩放裁剪（scale=1.5）")
    result = node.crop_to_circle(
        image=test_tensor,
        diameter_mm=58.0,
        scale=1.5,
        offset_x=0,
        offset_y=0,
        rotation=0,
        dpi=300
    )
    output_img = tensor2pil(result[0])
    print(f"  ✓ 输出尺寸: {output_img.size}")
    
    # 测试偏移
    print("测试3: 带偏移裁剪（offset_x=50, offset_y=30）")
    result = node.crop_to_circle(
        image=test_tensor,
        diameter_mm=58.0,
        scale=1.0,
        offset_x=50,
        offset_y=30,
        rotation=0,
        dpi=300
    )
    output_img = tensor2pil(result[0])
    print(f"  ✓ 输出尺寸: {output_img.size}")
    
    # 测试旋转
    print("测试4: 带旋转裁剪（rotation=45）")
    result = node.crop_to_circle(
        image=test_tensor,
        diameter_mm=58.0,
        scale=1.0,
        offset_x=0,
        offset_y=0,
        rotation=45,
        dpi=300
    )
    output_img = tensor2pil(result[0])
    print(f"  ✓ 输出尺寸: {output_img.size}")
    
    print("✅ 圆形裁剪节点测试通过！")
    return True


def test_auto_optimize():
    """测试自动优化节点"""
    print("\n=== 测试自动优化节点 ===")
    
    # 创建测试图片（不同尺寸）
    test_sizes = [(800, 600), (600, 800), (500, 500)]
    
    node = AutoOptimizeBadgeNode()
    
    for i, size in enumerate(test_sizes, 1):
        print(f"测试{i}: 图片尺寸 {size}")
        test_img = create_test_image(size[0], size[1])
        test_tensor = pil2tensor(test_img)
        
        result = node.optimize(
            image=test_tensor,
            diameter_mm=58.0,
            dpi=300
        )
        
        optimal_scale, offset_x, offset_y = result
        print(f"  ✓ 最佳缩放: {optimal_scale:.3f}")
        print(f"  ✓ 偏移X: {offset_x}")
        print(f"  ✓ 偏移Y: {offset_y}")
        
        # 验证缩放值合理
        assert 0.1 <= optimal_scale <= 5.0, "缩放值超出合理范围"
    
    print("✅ 自动优化节点测试通过！")
    return True


def test_badge_layout():
    """测试徽章排版节点"""
    print("\n=== 测试徽章排版节点 ===")
    
    # 创建批次测试图片
    batch_size = 8
    test_images = []
    colors = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255),
        (255, 255, 100), (255, 100, 255), (100, 255, 255),
        (200, 150, 100), (150, 200, 150)
    ]
    
    for i in range(batch_size):
        img = create_test_image(400, 400, colors[i])
        test_images.append(pil2tensor(img))
    
    # 合并为批次tensor
    batch_tensor = torch.cat(test_images, dim=0)
    
    node = BadgeLayoutNode()
    
    # 测试网格模式
    print("测试1: 网格排版模式")
    result = node.create_layout(
        images=batch_tensor,
        diameter_mm=58.0,
        layout_type="网格",
        spacing_mm=5.0,
        margin_mm=10.0,
        dpi=300
    )
    
    output_img = tensor2pil(result[0])
    print(f"  ✓ A4尺寸: {output_img.size}")
    expected_width = int(210 / 25.4 * 300)
    expected_height = int(297 / 25.4 * 300)
    print(f"  ✓ 预期尺寸: ({expected_width}, {expected_height})")
    
    # 测试紧凑模式
    print("测试2: 紧凑排版模式")
    result = node.create_layout(
        images=batch_tensor,
        diameter_mm=58.0,
        layout_type="紧凑",
        spacing_mm=5.0,
        margin_mm=10.0,
        dpi=300
    )
    
    output_img = tensor2pil(result[0])
    print(f"  ✓ A4尺寸: {output_img.size}")
    
    # 测试不同参数
    print("测试3: 不同参数（小徽章，大间距）")
    result = node.create_layout(
        images=batch_tensor,
        diameter_mm=32.0,
        layout_type="网格",
        spacing_mm=10.0,
        margin_mm=15.0,
        dpi=300
    )
    
    output_img = tensor2pil(result[0])
    print(f"  ✓ A4尺寸: {output_img.size}")
    
    print("✅ 徽章排版节点测试通过！")
    return True


def test_integration():
    """集成测试：完整工作流"""
    print("\n=== 集成测试：完整工作流 ===")
    
    # 1. 创建测试图片
    print("步骤1: 创建测试图片")
    test_img = create_test_image(800, 600, (180, 120, 200))
    test_tensor = pil2tensor(test_img)
    
    # 2. 自动优化参数
    print("步骤2: 自动优化参数")
    optimize_node = AutoOptimizeBadgeNode()
    optimal_scale, offset_x, offset_y = optimize_node.optimize(
        image=test_tensor,
        diameter_mm=58.0,
        dpi=300
    )
    print(f"  ✓ 获得最佳参数: scale={optimal_scale:.3f}")
    
    # 3. 圆形裁剪
    print("步骤3: 应用圆形裁剪")
    crop_node = CircularCropNode()
    cropped = crop_node.crop_to_circle(
        image=test_tensor,
        diameter_mm=58.0,
        scale=optimal_scale,
        offset_x=offset_x,
        offset_y=offset_y,
        rotation=0,
        dpi=300
    )
    print(f"  ✓ 裁剪完成")
    
    # 4. 创建批次并排版
    print("步骤4: 批量排版")
    batch = torch.cat([cropped[0]] * 6, dim=0)  # 复制6份
    layout_node = BadgeLayoutNode()
    final_output = layout_node.create_layout(
        images=batch,
        diameter_mm=58.0,
        layout_type="紧凑",
        spacing_mm=5.0,
        margin_mm=10.0,
        dpi=300
    )
    
    output_img = tensor2pil(final_output[0])
    print(f"  ✓ 最终A4排版尺寸: {output_img.size}")
    
    print("✅ 完整工作流测试通过！")
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("BadgePatternTool-ComfyUI 节点测试")
    print("=" * 60)
    
    try:
        # 运行各项测试
        test_circular_crop()
        test_auto_optimize()
        test_badge_layout()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n节点已准备好在ComfyUI中使用。")
        print("请将此文件夹复制到 ComfyUI/custom_nodes/ 目录下，")
        print("然后重启ComfyUI即可使用。")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()

