# Academic paper style

Use this style when the user selects academic paper, research figure, or paper-like schema styling. The reference is a white research figure with nested blue memory panels, a peach runtime component, serif headings, and labeled black arrows. Preserve that visual grammar, not its subject matter or exact layout.

## Visual language

| Role | Treatment |
|---|---|
| Canvas | White `#ffffff`, generous margins, no texture or visible grid |
| Main text and arrows | Black `#000000` |
| Secondary prose | Dark gray `#555555` |
| Group panel | Pale blue `#d5e2f0`, blue border `#7ca6d8` |
| Nested panel | Very pale blue `#edf3f9`, lighter blue border `#9dbde3` |
| Runtime or contrasting category | Pale peach `#ffe4c8`, black border |
| Technical token chip | Blue `#b7cfe8`, blue border `#7ca6d8`, small corner radius |
| Ordinary component | White, black outline |

Use blue and peach to distinguish meaningful categories. Name those categories in a compact horizontal legend below the figure. Do not assign fixed meanings such as "runtime" unless they fit the user's content. Category fills can repeat; keep at most two focal elements.

Use Times New Roman with Times and serif fallbacks for headings, prose, connector labels, and legend text. Use bold serif headings for containers and components. Reserve Menlo or Courier New with monospace fallback for file names, paths, code, and directory trees. Avoid uppercase editorial tags.

At a roughly 1000 px figure width, start with 28–32 px headings, 20–24 px body and connector labels, and 20–24 px code. Scale consistently for the intended output. Keep geometry and font sizes on the shared 4 px grid. Do not shrink labels to fit dense content.

## Composition

- Show ownership and scope with nested rounded panels. A white outer frame can enclose internal panels and actors. Keep frame strokes about 2 px and internal borders 1–2 px.
- Set container headings at the upper left. A heading can interrupt the outer frame using a separate white-filled native text cell. Reserve enough space so it does not collide with inner panels.
- Align related panels into a small number of rows and columns. Use whitespace and containment to explain structure before adding arrows.
- Use black orthogonal connectors with clear filled arrowheads. Straight horizontal and vertical paths are preferred. Use arrowheads at both ends only for a genuinely bidirectional relationship.
- Put short action labels near their paths, in sentence case. Keep the shared separate-label cells, white masks, clear gaps, and unique ports.
- Use small native token chips and editable directory-tree text only when technical details help explain the system. They are content inside a panel, not additional graph nodes unless they have independent relationships.
- Keep the legend outside the outer frame. Omit decorative icons, shadows, gradients, and faux paper textures.

## Native XML workflow

The bundled JSON builder emits editorial styling. It has no academic paper preset. Generate uncompressed XML directly with a safe XML library such as Python's `xml.etree.ElementTree`; never interpolate raw source labels into XML.

Use the builder output and [spec-format.md](spec-format.md) as structural references. Preserve `mxfile` metadata (`data-title`, `data-description`, `data-type`, `data-audience`, `data-detail`), one `diagram`, the `mxGraphModel`, root cells `0` and `1`, and explicit geometry. Set `background="#ffffff"`, `grid="0"`, and `gridSize="4"`.

Keep `data-role="node"` on semantic nodes, `data-role="connector"` on edges, and `data-role="edge-label"` plus `data-edge-id` on separate labels. Give container backgrounds `data-role="zone"`; use editable text cells for headings and `data-role="header"` for the figure title. Preserve focal metadata and count semantic components honestly rather than hiding them as primitives.

Typical component style:

```text
rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;fontFamily=Times New Roman;fontSize=24;fontStyle=1;shadow=0;glass=0;gradientColor=none;
```

Use the shared explicit ports and rounded orthogonal edge styles, with `strokeColor=#000000;strokeWidth=2;endArrow=block;endFill=1;`. Set `startArrow=block;startFill=1;` only for bidirectional edges. Keep edge `value` empty; preserve the action in `data-label` and a separate label cell.

Validate with `scripts/validate_drawio.py`, then open or render the `.drawio` file and inspect it at the intended output size. Structural validation does not establish visual fidelity. Check serif fallback, nested-panel padding, frame-title masks, code legibility, arrow direction, and legend meaning.
