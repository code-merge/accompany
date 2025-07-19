const glob = require("glob");

module.exports = {
  darkMode: "class",
  content: [
    ...glob.sync("../app/core/ui/**/*.{html,jinja2}"),
    ...glob.sync("../app/modules/**/ui/**/*.{html,jinja2}")
  ],
  safelist: [
    { pattern: /^bg-\[var\(--.*\) \]$/ },
    { pattern: /^text-\[var \(--.*\) \]$/ },
    { pattern: /^hover\:bg-\[var \(--.*\) \]$/ },
    { pattern: /^focus\:ring-\[var \(--.*\) \]$/ },
    { pattern: /^rounded-\[var \(--.*\) \]$/ }
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)"
      }
    }
  },
  plugins: []
}
