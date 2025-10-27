# AI Prompt Lab - Logo 使用指南

## 📦 Logo 文件说明

### 1. `logo.svg` - 主 Logo (200x200)
- **用途**: 网站主页、关于页面、宣传材料
- **特点**: 完整版，带背景、渐变和装饰元素
- **颜色**: 
  - 主色: `#6366F1` → `#8B5CF6` (靛蓝到紫色渐变)
  - 辅色: `#10B981` (绿色)
  - 文字: `#FFFFFF` (白色)

**预览效果**:
- 圆形背景带渐变
- 中央实验室烧杯
- 烧杯内有 "AI" 文字
- 两侧有代码括号装饰
- 液体中有气泡效果

**使用示例**:
```html
<img src="/logo.svg" alt="AI Prompt Lab" width="200" height="200">
```

---

### 2. `logo-simple.svg` - 简约版 (200x200)
- **用途**: 小尺寸显示、移动端、图标
- **特点**: 简化版，更清晰的线条
- **适用场景**: 
  - 社交媒体头像
  - 移动应用图标
  - 小尺寸展示

**预览效果**:
- 圆角方形背景
- 简化的烧杯图标
- 底部 "APL" 文字

**使用示例**:
```html
<img src="/logo-simple.svg" alt="APL" width="64" height="64">
```

---

### 3. `logo-horizontal.svg` - 横版 Logo (400x120)
- **用途**: 导航栏、页眉、横幅
- **特点**: 图标+文字组合，适合宽屏展示
- **组成**: 
  - 左侧: 圆形图标
  - 右侧: "AI Prompt Lab" 文字 + 标语

**预览效果**:
- 左侧圆形背景的烧杯图标
- 右侧 "AI Prompt" (靛蓝) + "Lab" (紫色)
- 底部标语: "Test, Compare, Optimize Your Prompts"

**使用示例**:
```html
<img src="/logo-horizontal.svg" alt="AI Prompt Lab" height="60">
```

**在导航栏中使用**:
```vue
<template>
  <div class="navbar">
    <img src="/logo-horizontal.svg" alt="AI Prompt Lab" class="logo" />
  </div>
</template>

<style scoped>
.logo {
  height: 48px;
  width: auto;
}
</style>
```

---

### 4. `favicon.svg` - 网站图标 (32x32)
- **用途**: 浏览器标签页图标
- **特点**: 极简版，32x32 像素优化
- **已在 `index.html` 中配置**

**配置代码**:
```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

---

## 🎨 颜色规范

### 主色调
```css
--primary-indigo: #6366F1;    /* 靛蓝 - 主色 */
--primary-purple: #8B5CF6;    /* 紫色 - 主色渐变终点 */
--accent-green: #10B981;      /* 绿色 - 点缀色 */
--text-dark: #1F2937;         /* 深灰 - 标题文字 */
--text-light: #6B7280;        /* 浅灰 - 副标题文字 */
```

### 渐变组合
```css
background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
```

---

## 💡 使用建议

### 在 Vue 组件中使用

**方式 1: 直接引用**
```vue
<template>
  <img src="/logo.svg" alt="AI Prompt Lab" />
</template>
```

**方式 2: 作为背景**
```vue
<template>
  <div class="logo-container"></div>
</template>

<style scoped>
.logo-container {
  width: 200px;
  height: 200px;
  background-image: url('/logo.svg');
  background-size: contain;
  background-repeat: no-repeat;
}
</style>
```

**方式 3: 内联 SVG (可修改颜色)**
```vue
<template>
  <div v-html="logoSvg"></div>
</template>

<script setup>
import { ref } from 'vue'
// 可以动态修改 SVG 内容
</script>
```

---

## 📱 响应式使用

```vue
<template>
  <picture>
    <!-- 移动端显示简约版 -->
    <source media="(max-width: 768px)" srcset="/logo-simple.svg">
    <!-- 桌面端显示完整版 -->
    <img src="/logo.svg" alt="AI Prompt Lab">
  </picture>
</template>
```

---

## 🚀 导出其他格式

如果需要 PNG 或其他格式:

### 在线转换
1. 访问 https://cloudconvert.com/svg-to-png
2. 上传 SVG 文件
3. 选择尺寸(建议 512x512 或 1024x1024)
4. 下载 PNG

### 推荐尺寸
- **Favicon**: 32x32, 64x64
- **社交媒体**: 512x512, 1024x1024
- **App 图标**: 512x512, 1024x1024
- **印刷**: 矢量格式(保持 SVG)

---

## 📋 品牌一致性

### ✅ 正确使用
- 保持 Logo 比例不变
- 使用官方颜色
- 周围留有足够空白(至少 Logo 高度的 10%)
- 在深色背景上使用主 Logo

### ❌ 避免使用
- 不要拉伸或压缩 Logo
- 不要修改颜色
- 不要添加阴影或特效
- 不要旋转 Logo
- 不要在 Logo 上叠加文字

---

## 🎯 典型应用场景

| 场景 | 推荐 Logo | 尺寸 |
|------|----------|------|
| 网站首页 | logo.svg | 200px |
| 导航栏 | logo-horizontal.svg | 48-60px 高 |
| 浏览器标签 | favicon.svg | 自动 |
| 社交媒体头像 | logo-simple.svg | 512x512 |
| GitHub README | logo.svg | 200-300px |
| 移动应用 | logo-simple.svg | 512x512 |
| 打印材料 | logo.svg | 矢量 |

---

## 📝 更新日志

- **2025-10-27**: 初始版本，创建 4 个 Logo 变体
  - 主 Logo (完整版)
  - 简约版
  - 横版
  - Favicon

---

**设计理念**: 
Logo 以实验室烧杯为核心元素，象征 AI Prompt Lab 的测试和优化功能。烧杯内的 "AI" 文字和绿色液体代表 AI 技术和创新。整体采用科技感的靛蓝-紫色渐变，传达专业、现代的品牌形象。

