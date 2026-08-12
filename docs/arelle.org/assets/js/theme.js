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

  const tabs = [...document.querySelectorAll('[role=tab]')]
  const panels = tabs.map((tab) => document.getElementById(tab.dataset.panel))
  const activateTab = (tab, focus) => {
    tabs.forEach((other, index) => {
      const selected = other === tab
      other.ariaSelected = selected
      other.tabIndex = selected ? 0 : -1
      panels[index].hidden = !selected
    })
    if (focus) {
      tab.parentNode.scrollLeft = tab.offsetLeft - tabs[0].offsetLeft
      tab.focus({ preventScroll: true })
    }
  }
  tabs.forEach((tab, index) => {
    tab.onclick = () => activateTab(tab, true)
    tab.onkeydown = (event) => {
      const key = event.key
      const step = key[5] === 'L' ? -1 : key[5] === 'R' ? 1 : 0
      const next = step
        ? tabs[(index + step + tabs.length) % tabs.length]
        : key[0] === 'H' ? tabs[0] : key[0] === 'E' ? tabs[tabs.length - 1] : null
      if (!next) return
      event.preventDefault()
      activateTab(next, true)
    }
  })
  tabs[0] && activateTab(tabs[0])
})
