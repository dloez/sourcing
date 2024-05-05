import esbuild from "esbuild"
import process from "process"
import builtins from "builtin-modules"
import { copy } from "esbuild-plugin-copy"

const prod = process.argv[2] === "production"

const context = await esbuild.context({
  entryPoints: ["./src/main.ts"],
  bundle: true,
  external: [
    "obsidian",
    "electron",
    "@codemirror/autocomplete",
    "@codemirror/collab",
    "@codemirror/commands",
    "@codemirror/language",
    "@codemirror/lint",
    "@codemirror/search",
    "@codemirror/state",
    "@codemirror/view",
    "@lezer/common",
    "@lezer/highlight",
    "@lezer/lr",
    ...builtins,
  ],
  format: "cjs",
  target: "es2018",
  logLevel: "info",
  sourcemap: prod ? false : "inline",
  treeShaking: true,
  outdir: "./sourcing-obsidian-plugin",
  plugins: [
    copy({
      resolveFrom: "cwd",
      assets: [
        {
          from: ["./manifest.json"],
          to: ["./sourcing-obsidian-plugin/manifest.json"],
          watch: true,
        },
        {
          from: ["./styles.css"],
          to: ["./sourcing-obsidian-plugin/styles.css"],
          watch: true,
        },
      ],
    }),
  ],
})

if (prod) {
  await context.rebuild()
  process.exit(0)
} else {
  await context.watch()
}
