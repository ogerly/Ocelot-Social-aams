# WP-006 — Styleguide & Design System Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

The platform has undergone a **design system migration** from a legacy styleguide to a modern component library. This migration is 89% complete.

| System | Package | Status |
|---|---|---|
| Legacy | `@human-connection/styleguide` 0.5.22 | **Retired** (removed from webapp deps) |
| Current | `@ocelot-social/ui` 0.0.1 | **Active** (linked via `file:../packages/ui`) |

---

## 2. Legacy Styleguide (`@human-connection/styleguide`)

### Architecture

| Aspect | Detail |
|---|---|
| Package | `@human-connection/styleguide` v0.5.22 |
| Build Tool | Vue CLI 3 (`@vue/cli-service ~3.11.0`) |
| Output | UMD library (`dist/system.umd.min.js`) |
| Vue | Vue 2.6 (Options API) |
| Design Tokens | Theo 8.1 (Salesforce) — `.yml` → SCSS/JSON |
| SCSS System | Global inject `shared.scss` via `additionalData` |
| Icon System | 200+ SVG files, compiled via `vue-svg-loader` |
| Component Prefix | `Ds` (e.g., `DsButton`, `DsIcon`, `DsCard`) |

### Component Inventory

| Category | Components |
|---|---|
| **Data Display** | DsAvatar, DsCopyField, DsList, DsNumber, DsTable |
| **Data Input** | DsForm, DsFormItem, DsInput, DsRadio, DsSelect |
| **Layout** | DsCard, DsContainer, DsFlex, DsGrid, DsModal, DsPage, DsPageTitle, DsPlaceholder, DsSection, DsSpace, DsSpinner |
| **Navigation** | DsButton, DsMenu |
| **Typography** | DsChip, DsCode, DsHeading, DsIcon, DsLogo, DsTag, DsText |

### Token System (Theo)

- 18 token YAML files compiled via Theo
- Color palette: HSL-based, 7-tone neutral scale (0–100) + primary (green) + secondary (blue) + danger (red) + warning (orange) + success + yellow
- Output: `tokens.scss`, `tokens.map.scss`, `tokens.raw.json`, `tokens.json`
- Spacing: token-based `getSpace()` utility
- Media queries: responsive mixin from design tokens

### Current Status

**Fully retired.** Not listed in `webapp/package.json`. Design tokens extracted locally to `webapp/assets/_new/styles/_styleguide-tokens.scss`. No `ds-*` component tags remain in the codebase.

---

## 3. New UI Library (`@ocelot-social/ui`)

### Architecture

| Aspect | Detail |
|---|---|
| Package | `@ocelot-social/ui` v0.0.1 |
| Build Tool | Vite 7.3 |
| Vue Support | Vue 2.7+ and Vue 3 (via `vue-demi` 0.14) |
| CSS Framework | Tailwind CSS 4 |
| Variant System | CVA (`class-variance-authority` 0.7) + `clsx` + `tailwind-merge` |
| Type Safety | Full TypeScript, `.d.ts` generation via `vite-plugin-dts` |
| Storybook | v10.2 (visual documentation) |
| Testing | Vitest 4.0 (unit) + Playwright 1.58 (visual regression) |
| Size Limits | index < 20kB, style.css < 5kB (brotli) |
| Component Prefix | `Os` (e.g., `OsButton`, `OsIcon`, `OsCard`) |

### Module Exports

```
@ocelot-social/ui          → Components, plugin, utils, types  
@ocelot-social/ui/ocelot   → Migration icons (72 SVGs, temporary)
@ocelot-social/ui/style.css → CSS variables + theme + utilities
@ocelot-social/ui/tailwind.preset → CSS variable contract
```

### Component Inventory

| Component | Features | Replaces |
|---|---|---|
| **OsButton** | 7 variants × 3 appearances × 4 sizes, polymorphic `as`, loading, circle, slots (icon, suffix) | DsButton |
| **OsIcon** | System icons (3 built-in) + 72 ocelot icons, size xs–2xl, a11y | DsIcon |
| **OsSpinner** | CSS animation, size variants | DsSpinner |
| **OsCard** | Polymorphic tag, highlight, heroImage slot | DsCard |
| **OsBadge** | Variant/size/shape matrix, pill/square | DsChip + DsTag |
| **OsNumber** | Animated count-up (requestAnimationFrame, easeOut) | DsNumber |
| **OsModal** | Focus trap, body scroll lock, backdrop, keyboard (Escape), confirm/cancel | DsModal |
| **OsMenu + OsMenuItem** | Route-based, dropdown, custom matcher, scoped slots | DsMenu |

### CVA Pattern (Standard Component Architecture)

```typescript
// button.variants.ts
import { cva } from 'class-variance-authority'

export const buttonVariants = cva('base-classes', {
  variants: {
    variant: { default: '...', primary: '...', danger: '...' },
    appearance: { filled: '...', outline: '...', ghost: '...' },
    size: { sm: '...', md: '...', lg: '...', xl: '...' },
  },
  compoundVariants: [
    { variant: 'primary', appearance: 'filled', class: '...' },
    // ... 7×3 = 21 compound variants with hover/active/disabled
  ],
  defaultVariants: { variant: 'default', appearance: 'filled', size: 'md' },
})
```

### CSS Custom Properties Contract

The library uses CSS Custom Properties for theming:
```css
--color-default, --color-primary, --color-secondary,
--color-danger, --color-warning, --color-success, --color-info,
--color-disabled, --color-text, --font-family-base
```

Consumers provide these values. In Ocelot, `ocelot-ui-variables.scss` bridges legacy SCSS vars → CSS Custom Properties.

### Icon System

- **Built-in system icons**: check, close, plus (via Vite `?icon` transform → render functions)
- **Migration icons**: 72 ocelot-specific SVGs in `@ocelot-social/ui/ocelot` (temporary, bridge from legacy 200+ icon set)
- **Branding override**: Webapp merges `ocelotIcons` with local branding SVGs, branding wins on conflict

---

## 4. Migration Status

### Overall: 89% Complete (85/96 tasks)

| Migration Task | Status |
|---|---|
| DsButton → OsButton (133 uses) | ✅ Complete |
| DsIcon → OsIcon | ✅ Complete |
| DsSpinner → OsSpinner | ✅ Complete |
| DsCard → OsCard | ✅ Complete |
| DsChip → OsBadge pill (20 uses) | ✅ Complete |
| DsTag → OsBadge square (3 uses) | ✅ Complete |
| DsNumber → OsNumber (5 uses) | ✅ Complete |
| DsModal → OsModal (7 uses) | ✅ Complete |
| DsMenu → OsMenu/OsMenuItem (17 uses) | ✅ Complete |
| DsInput → OcelotInput (23 files, webapp-local) | ✅ Complete |
| DsSelect → OcelotSelect (3 files, webapp-local) | ✅ Complete |
| DsForm → formValidation mixin | ✅ Decoupled |
| 13 layout/typography wrappers → plain HTML | ✅ Complete |
| DsRadio → native `<input type="radio">` | ✅ Complete |
| **`ds-*` tags remaining**: 0 | ✅ Clean |

### Remaining Work (11/96 tasks)

- Token system finalization (remove legacy SCSS variables)
- Complete Storybook documentation
- Visual regression baseline capture
- Publish to npm registry
- Remove `styleguide/` directory entirely

---

## 5. Integration in Webapp

### CSS Loading Chain (nuxt.config.js)

```
1. reset.scss                       ← Normalize/reset
2. main.scss                        ← Legacy layout styles
3. branding/                        ← White-label overrides
4. ocelot-ui-variables.scss         ← SCSS → CSS Custom Properties bridge
5. ds-compat.scss                   ← Legacy compatibility
6. @ocelot-social/ui/style.css      ← New library styles
```

### Webpack Configuration

- `transpile: ['vue-demi', '@ocelot-social/ui']` (Nuxt build)
- Aliases resolve `@ocelot-social/ui` → `../packages/ui/dist/*.mjs`

### Test Mocking

- `test/__mocks__/@ocelot-social/ui.js` — Jest mock for components
- `test/__mocks__/@ocelot-social/ui/ocelot.js` — Jest mock for icons

### Active Usage (50+ files)

| Component | Usage Count |
|---|---|
| OsButton | 30+ files |
| OsIcon | 30+ files |
| OsCard | 6+ files |
| OsBadge | 2+ files |
| OsMenu/OsMenuItem | 1 file |
| OsNumber | 1 file |

---

## 6. Architectural Decisions

| Decision | Rationale |
|---|---|
| **Vue 2.7 + 3 dual support** via `vue-demi` | Enables incremental Vue 3 migration without blocking UI updates |
| **Tailwind CSS 4** over SCSS | Modern utility-first CSS, smaller bundle, better DX |
| **CVA** for variant management | Type-safe, composable, works with Tailwind class merging |
| **CSS Custom Properties** for theming | Framework-agnostic, runtime switchable, cascade-friendly |
| **Monorepo link** (`file:../packages/ui`) | No publish cycle during development, instant feedback |
| **72 migration icons** (temporary) | Pragmatic bridge — ship now, clean up after Vue 3 migration |
| **Webapp-local form components** | OcelotInput/OcelotSelect in webapp, not in library (too app-specific) |

---

## 7. Risk Assessment

| Risk | Severity | Detail |
|---|---|---|
| `vue-demi` compatibility at scale | **MEDIUM** | Render function differences Vue 2.7 vs 3 may surface in edge cases |
| Token bridge fragility | **LOW** | SCSS → CSS Custom Property mapping is manual, could drift |
| Icon gap (200 → 72) | **LOW** | Missing icons replaced by branding override or removed |
| Storybook 10 stability | **LOW** | Very new version, but isolated in dev |
| `styleguide/` cleanup | **LOW** | Dead code remains in repo, increases clone size |
