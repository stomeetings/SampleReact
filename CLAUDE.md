# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a minimal Vite + React scaffold (JavaScript, not TypeScript) used for learning/experimenting with React fundamentals. There is no router, state library, backend, or test framework configured — it's just the Vite React template plus a handful of tutorial components exploring function components and `useState`.

## Commands

- `npm run dev` — start the Vite dev server with HMR
- `npm run build` — production build (output to `dist/`)
- `npm run preview` — serve the production build locally
- `npm run lint` — run ESLint over the project

There is no test runner configured in this repo.

## Architecture

- Entry point: `src/main.jsx` mounts `<App />` into `#root` (see `index.html`) inside `StrictMode`.
- `src/App.jsx` is the top-level component; it currently just renders each tutorial component one after another (`CompFun`, `NeCompo`, `CounterCheck`, etc.) — there's no routing or composition logic beyond that.
- Each tutorial component lives in its own file at `src/` root (not in a `components/` subfolder): `CompFun.jsx`, `NeCompo.jsx`, `CounterCheck.jsx`. New example components generally follow this same flat, one-file-per-component pattern and get wired into `App.jsx` by importing and rendering them.
- Styling is plain CSS (`App.css`, `index.css`), imported directly into components — no CSS-in-JS or Tailwind.
- ESLint config (`eslint.config.js`) uses the flat-config format with `js.configs.recommended`, `eslint-plugin-react-hooks`, and `eslint-plugin-react-refresh`. Note the custom rule: `no-unused-vars` ignores variables matching `^[A-Z_]` (e.g. constants/components), so unused-var errors on lowercase names are real signals, not lint noise.
