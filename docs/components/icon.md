# 🖼️ Icon Component

Reusable macro for rendering inline SVG icons in your ERP system using TailwindCSS and Jinja2.

---

## 📦 Location

`app/core/ui/components/icon.html`

---

## 🎯 Purpose

- Render SVG icons inline using Tailwind utility classes.
- Support customizable size, stroke width, and theming.
- Load icons from module-specific or centralized paths.
- Avoid sprite injection or raw HTML SVG pasting.

---

## 🔧 Macro Signature

```jinja2
{% macro icon(name, size="1rem", stroke="2", extra_classes="", path=None) %}
```

## 📋 Parameters

Name	Type	Default	Description
name	string	—	Icon name (without .svg extension)
size	string	"1rem"	Width and height of icon (px, rem, etc.)
stroke	string	"2"	Stroke width of the icon paths
extra_classes	string	""	Additional Tailwind CSS classes
path	string	None	Jinja-relative path to icon file. Defaults to core icon path


### 🧪 Usage Examples

#### ✅ Example: Load from Shared Icon Directory

```jinja2
{% from "core/ui/components/icon.html" import icon %}
{{ icon(name="trash") }}
```
Loads from: core/ui/icons/trash.svg

#### ✅ Example: Load from Module-Specific Path

```jinja2
{{ icon(
  name="handshake",
  path="modules/onboarding/ui/icons/handshake.svg",
  size="1.25rem",
  extra_classes="text-blue-600"
) }}
```

Loads from module directory with custom size and color.

### 🔒 Requirements

Icon SVG files must contain only `<path>` or `<g>` — no `<svg>` wrappers.

Path must be resolvable through Jinja `TEMPLATE_DIRS`.

### ✅ Best Practices

- Keep SVGs modular: per-feature storage (onboarding/ui/icons/ etc.)
- Use macros over raw SVG injection to enable consistent styling.
- Avoid .svg extension in name — add extension via macro logic if needed.
