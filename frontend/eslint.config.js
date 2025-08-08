import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";
import { globalIgnores } from "eslint/config";

export default tseslint.config(globalIgnores(["dist"]), {
  files: ["**/*.{ts,tsx}"],
  extends: [
    // Base JS rules
    js.configs.recommended,

    // Type-aware rules: pick one of the following three lines
    // ...tseslint.configs.recommendedTypeChecked,
    // ...tseslint.configs.strictTypeChecked, // stricter
    ...tseslint.configs.stylisticTypeChecked, // stylistic layer (optional)
    // You can combine strictTypeChecked + stylisticTypeChecked if you want both:
    // ...tseslint.configs.strictTypeChecked,
    // ...tseslint.configs.stylisticTypeChecked,

    // React hooks + Vite Fast Refresh safeties
    reactHooks.configs["recommended-latest"],
    reactRefresh.configs.vite,

    // React-specific rules (component patterns, DOM usage)
    reactX.configs["recommended-typescript"],
    reactDom.configs.recommended,
  ],
  languageOptions: {
    ecmaVersion: 2022,
    globals: globals.browser,
    parserOptions: {
      // Important: point ESLint at your TS projects for type-aware rules
      project: ["./tsconfig.app.json", "./tsconfig.node.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
  settings: {
    react: { version: "detect" },
  },
  rules: {
    // Common niceties; tweak to taste
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
  },
});
