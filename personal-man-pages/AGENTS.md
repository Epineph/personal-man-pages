# Working on this repository

- Keep this a small, local-first repository of Markdown help pages.
- Read README.md and registry.json before changing links or the page format.
- Preserve stable page IDs. Aliases and file paths can change independently.
- Keep ordinary --help short; advertise long, detailed, technical and examples
  views. Do not reserve a script's existing --all option automatically.
- Keep headings and depth appropriate to the command. Technical views are
  optional. Practical help must state important operational assumptions.
- Use two-space indentation, clear section comments and an 81-column target.
- Keep the core free of third-party Python dependencies. Pandoc, a PDF engine
  and Glow are optional feature dependencies; do not auto-install them.
- Update page content when changing an example command's arguments.
- Run python3 bin/pman --check and relevant unittest checks after changes.
- Use official sources with review dates for native-command documentation.
- Do not publish, change GitHub visibility, or choose a license automatically.
