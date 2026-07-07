---
description: Create a UI component in /components/ui
argument-hint: component name | component summary
---

Create a new reusable UI component under `src/components/ui/` based on the argument: `$ARGUMENTS`.

The argument may be either a component name (e.g. `Button`) or a short summary of what it should do (e.g. `a dismissible alert banner`). If it's a summary rather than a bare name, pick a concise PascalCase component name that fits it.

Steps:
1. If `src/components/ui/` doesn't exist yet, create it.
2. Create `src/components/ui/<Name>.jsx` as a plain function component (no TypeScript, no PropTypes — this project uses neither):
   - Named function declaration, default export at the bottom (matches `src/CounterCheck.jsx`, `src/ThemeToggle.jsx`).
   - Single quotes, no semicolons, 2-space indentation — match the existing style in `src/App.jsx`.
   - Destructure any obvious props directly in the function signature; don't add PropTypes or default values unless the summary implies specific required inputs.
   - Only add `useState`/other hooks if the summary clearly implies interactive/stateful behavior.
3. Do not wire the component into `App.jsx` — components in `components/ui/` are reusable primitives, not the tutorial demos already rendered there.
4. Do not create a CSS file or test file unless asked — this repo has no test runner and styling is plain CSS imported per-component only where already established.
5. Keep it minimal: implement only what the name/summary calls for, no extra props, variants, or configuration beyond that.
