const root = document.documentElement
const storageKey = 'ixbrl-viewer-theme'
const darkScheme = matchMedia('(prefers-color-scheme: dark)')

let savedTheme
try {
  savedTheme = localStorage.getItem(storageKey)
} catch {}

if (savedTheme === 'light' || savedTheme === 'dark') {
  root.dataset.theme = savedTheme
}

const isDark = () => (
  root.dataset.theme ? root.dataset.theme === 'dark' : darkScheme.matches
)

addEventListener('DOMContentLoaded', () => {
  const button = document.querySelector('[data-theme-toggle]')
  if (!button) return

  const updateLabel = () => {
    const label = isDark() ? 'Switch to light' : 'Switch to dark'
    button.ariaLabel = label
    button.title = label
  }

  button.addEventListener('click', () => {
    const theme = isDark() ? 'light' : 'dark'
    root.dataset.theme = theme
    try {
      localStorage.setItem(storageKey, theme)
    } catch {}
    updateLabel()
  })

  darkScheme.addEventListener('change', updateLabel)
  updateLabel()
})
