# 🎨 Centralized Icon System

This document explains how to use the centralized Google Material Icons system in the AI Refinement Dashboard.

## 📋 Overview

The project uses [Google Material Icons](https://fonts.google.com/icons) with a centralized CSS system for consistent styling and easy maintenance.

## 🚀 Quick Start

### Basic Usage
```html
<!-- Simple icon -->
<span class="material-icons-round">home</span>

<!-- Icon with size -->
<span class="material-icons-round icon-lg">dashboard</span>

<!-- Icon with color -->
<span class="material-icons-round icon-primary">play_arrow</span>

<!-- Icon with multiple classes -->
<span class="material-icons-round icon-lg icon-success icon-hover">check_circle</span>
```

### Using the Icon Component
```vue
<template>
  <!-- Basic usage -->
  <Icon name="home" />
  
  <!-- With props -->
  <Icon name="play_arrow" size="lg" color="primary" hover />
  
  <!-- Spinning icon -->
  <Icon name="refresh" spin />
</template>

<script>
import Icon from '@/components/Icon.vue'
</script>
```

## 🎯 Available Classes

### Sizes
- `.icon-xs` - 16px
- `.icon-sm` - 20px  
- `.icon-md` - 24px (default)
- `.icon-lg` - 32px
- `.icon-xl` - 48px
- `.icon-xxl` - 64px

### Colors
- `.icon-primary` - Primary blue
- `.icon-secondary` - Secondary gray
- `.icon-success` - Success green
- `.icon-info` - Info cyan
- `.icon-warning` - Warning yellow
- `.icon-danger` - Danger red
- `.icon-light` - Light gray
- `.icon-dark` - Dark gray
- `.icon-muted` - Muted text color

### States
- `.icon-hover` - Scale on hover
- `.icon-spin` - Continuous rotation

## 🏗️ Context-Specific Classes

### Cards
```html
<div class="card-icon">
  <span class="material-icons-round">psychology</span>
</div>
```

### Navigation
```html
<span class="nav-icon material-icons-round">home</span>
```

### Lists
```html
<span class="list-icon material-icons-round">folder</span>
```

### Status Indicators
```html
<span class="status-icon success">
  <span class="material-icons-round">check_circle</span>
</span>
```

### Buttons
```html
<button class="btn">
  <span class="material-icons-round">save</span>
  Save
</button>
```

### Alerts
```html
<div class="alert alert-success">
  <span class="alert-icon success material-icons-round">check_circle</span>
  Success message
</div>
```

## 🎨 Common Icon Patterns

### Icon Groups
```html
<div class="icon-group">
  <span class="material-icons-round icon-primary">play_arrow</span>
  <span class="material-icons-round icon-success">check_circle</span>
  <span class="material-icons-round icon-danger">error</span>
</div>
```

### Icon with Text
```html
<div class="icon-text">
  <span class="material-icons-round">upload</span>
  <span>Upload Dataset</span>
</div>
```

### Status with Icon
```html
<div class="status-indicator">
  <span class="status-icon success">
    <span class="material-icons-round">check_circle</span>
  </span>
  <span>Training Complete</span>
</div>
```

## 🤖 AI Dashboard Specific Icons

### Training & Models
- `model_training` - Model training
- `psychology` - AI/ML
- `auto_awesome` - AI enhancement
- `memory` - Memory/context
- `precision_manufacturing` - Fine-tuning

### Data Management
- `dataset` - Dataset
- `folder` - Data folder
- `storage` - Data storage
- `cloud_upload` - Cloud upload
- `table_chart` - Data visualization

### Actions
- `play_arrow` - Start/run
- `pause` - Pause
- `stop` - Stop
- `refresh` - Refresh
- `rocket_launch` - Deploy

### Status
- `check_circle` - Success
- `error` - Error
- `warning` - Warning
- `info` - Information
- `pending` - Pending

## 📱 Responsive Considerations

Icons automatically scale with the neumorphic design system and maintain consistency across different screen sizes.

## 🎯 Best Practices

1. **Consistency**: Use the same icon for the same action across the app
2. **Semantic**: Choose icons that clearly represent their function
3. **Accessibility**: Icons should have accompanying text when possible
4. **Performance**: Icons are loaded once and cached by the browser
5. **Maintenance**: Use the centralized classes for easy updates

## 🔧 Customization

To add new icon styles, extend the CSS in `src/assets/main.css`:

```css
/* Custom icon style */
.my-custom-icon {
  font-size: 28px;
  color: #custom-color;
  transform: rotate(45deg);
}
```

## 📚 Resources

- [Google Material Icons](https://fonts.google.com/icons) - Browse all available icons
- [Material Design Icons](https://material.io/design/iconography/system-icons.html) - Design guidelines
- [Icon Usage Guidelines](https://material.io/design/iconography/product-icons.html) - Best practices

---

*This icon system ensures consistent, accessible, and maintainable iconography throughout the AI Refinement Dashboard.*
