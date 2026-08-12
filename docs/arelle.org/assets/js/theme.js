const root = document.documentElement
const themeData = root.dataset
const storageKey = 'ixbrl-viewer-theme'
const darkScheme = matchMedia('(prefers-color-scheme: dark)')

try {
  const savedTheme = localStorage.getItem(storageKey)
  if (savedTheme === 'light' || savedTheme === 'dark') themeData.theme = savedTheme
} catch {}

const isDark = () => themeData.theme ? themeData.theme === 'dark' : darkScheme.matches

addEventListener('DOMContentLoaded', () => {
  const button = document.querySelector('[data-theme-toggle]')
  const updateLabel = () => button.ariaLabel = button.title = isDark() ? 'Switch to light' : 'Switch to dark'
  button.onclick = () => {
    const theme = isDark() ? 'light' : 'dark'
    themeData.theme = theme
    try {
      localStorage.setItem(storageKey, theme)
    } catch {}
    updateLabel()
  }
  darkScheme.onchange = updateLabel
  updateLabel()
})
