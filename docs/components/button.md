# 🔘 Button Component

Macro-based utility button supporting icons, size and variant options, accessibility, loading state, and HTMX-ready attributes.

---

## 📦 Location

`app/core/ui/components/button.html`

---

## 🎯 Purpose

- Render styled buttons with Tailwind utility classes.
- Support size variants, theme tokens, disabled/loading states.
- Dynamically inject icons using `icon.html`.
- Pass arbitrary HTML attributes (`hx-*`, `aria-*`, etc.) for interactivity.

---

## 🔧 Macro Signature

```jinja2
{% macro button(label="", icon_name="", icon_path=None, size="md", variant="primary", type="button", disabled=false, loading=false, extra_classes="", attrs={}) %}
```


## 📋 Parameters

Name	Type	Default	Description
label	string	""	Visible button text
icon_name	string	None	Icon name to pass to icon() macro
icon_path	string	None	Path to SVG file (module-specific or shared)
size	string	"md"	Size variant: "sm", "md", "lg"
variant	string	"primary"	Style variant: "primary", "secondary", "ghost"
type	string	"button"	HTML button type attribute
disabled	boolean	false	Whether the button is disabled
loading	boolean	false	Whether to show spinner loading indicator
extra_classes	string	""	Additional Tailwind CSS classes
attrs	dict	{}	Arbitrary HTML attributes like hx-*, data-*, aria-*


## 🎨 Styling Details

- Dynamic composition via Tailwind classes:

- Size map: `px-3 py-2`, `text-sm`, etc.

- Variant map: theme tokens like `bg-[var(--primary)]`

- Hover and focus states baked into macro logic

- Colors pulled from your `theme.css` tokens


## 🧪 Usage Examples

#### ✅ Basic Submit Button

```jinja2
{{ button(label="Submit") }}
```

#### ✅ Icon Button with Module-Specific Icon

```jinja2
{{ button(
  label="Connect",
  icon_name="handshake",
  icon_path="modules/onboarding/ui/icons/handshake.svg",
  variant="primary",
  size="lg"
) }}
```

#### ✅ HTMX Button

```jinja2
{{ button(
  label="Refresh",
  variant="ghost",
  attrs={
    "hx-get": "/api/data",
    "hx-target": "#output",
    "hx-swap": "outerHTML"
  }
) }}
```

#### ✅ Loading and Disabled Button

```jinja2
{{ button(
  label="Saving...",
  loading=true,
  disabled=true
) }}
```

### 🛡️ Accessibility

- Auto aria-label from label

- `role="button"` by default

- `focus:outline-none` and `focus:ring-[var(--ring)]`

- `disabled` disables pointer events and opacity


## ✅ Best Practices

- Keep styling declarative in macro logic — no CSS file changes needed.

- Use theme tokens via `theme.css` (`--primary`, `--accent`, etc.)

- Centralize icon logic in `icon.html` for reusability

- Tailwind purge-safe setup: use safelist patterns if needed