# Draw.io design contract

## Authority

When installed beside `diagram-design`, its current `references/style-guide.md` overrides the fallback values below. Read its selected type reference as the diagram grammar. Translate intent into Draw.io cells; do not imitate browser SVG implementation details that have no Draw.io equivalent.

## Fallback light tokens

| Role | Value | Draw.io use |
|---|---|---|
| paper | `#f5f5f5` | page and label-mask fill |
| paper-2 | `#ececec` | optional framed region |
| ink | `#2d3142` | primary text and stroke |
| muted | `#4f5d75` | secondary text and connectors |
| soft | `#7a8399` | sublabels and quiet boundaries |
| rule | `#d9dade` | hairline borders |
| rule-solid | `#bfc0c0` | stronger separators |
| accent | `#eb6c36` | at most 2 focal elements |
| accent-tint | `#fcefe9` | focal fill |
| link | `#2e5aa8` | HTTP, API, or external flow |

Draw.io does not reliably preserve alpha color values across all editors. Use the opaque approximations above for native cells.

## Typography

| Role | Family | Size | Weight |
|---|---|---:|---:|
| page title | Instrument Serif | 28 | 400 |
| node name | Geist | 12 | 600 |
| sublabel | Geist Mono | 8 | 400 |
| eyebrow or tag | Geist Mono | 8 | 500 |
| connector label | Geist Mono | 8 | 400 |
| callout | Instrument Serif Italic | 14 | 400 |

Use HTML labels for mixed typography inside a native shape. Draw.io may display a system fallback if a font is not installed; preserve the intended family in the file. Never replace all text with monospace.

## Native cell mapping

| Semantic kind | Native shape and treatment |
|---|---|
| focal | rounded rectangle, `accent-tint` fill, `accent` stroke |
| backend / API / step | rounded rectangle, white fill, `ink` stroke |
| store / state | cylinder or rounded rectangle, pale ink fill, `muted` stroke |
| external / cloud | rounded rectangle or cloud, quiet grey fill, soft stroke |
| input / user | rounded rectangle or actor, muted tint, soft stroke |
| optional / async | pale fill, soft dashed stroke |
| security / boundary | pale accent fill, accent dashed stroke |
| decision | rhombus using the same semantic color role as its importance |
| zone | rounded background rectangle, 2% ink wash approximation, quiet border |

Maximum radius is visually equivalent to 6–8 px. Use `arcSize=8`; never use pill-like nodes.

## Connector contract

- Use `edgeStyle=orthogonalEdgeStyle`, `rounded=1`, `curved=0`, and an end arrow.
- Use `strokeColor=#4f5d75` for internal flow, `#2e5aa8` for external/API flow, and `#eb6c36` for one primary highlighted flow.
- Use `dashed=1;dashPattern=4 3` for optional, passive, return, or async flow.
- Store labels in separate vertex cells with `fillColor=#f5f5f5`, no border, and a `data-edge-id` attribute. The edge cell value remains empty.
- Use explicit `exitX`, `exitY`, `entryX`, and `entryY`. Never let two connectors share the same source-edge or target-edge attachment.
- Add explicit waypoints where automatic orthogonal routing might cross a box, overlap another connector, or obscure a label.
- Prefer a layout without crossings. When a crossing is unavoidable, use Draw.io's line-jump style on the less important connector and verify the editor preserves it.

## Layer order

Order cells in the XML as:

1. page/header text;
2. zones and boundaries;
3. connectors;
4. connector-label masks;
5. nodes and data primitives;
6. legend separator and legend items.

This keeps connectors behind endpoint boxes while labels remain readable.

## 4 px grid and budgets

- Coordinates, dimensions, gaps, and font sizes use multiples of 4.
- Standard limit: 9 semantic nodes and 12 connectors.
- Imported `faithful` mode may use up to 24 nodes only when zoned; split above 24.
- Keep at most 2 focal elements.
- Use at most 3 architecture zones, 5 lanes, 5 sequence lifelines, 8 ER entities, or the stricter limit in the sibling type reference.

## Visual inspection gate

Reject the output if any of these are true:

- a diagonal connector appears between off-axis nodes;
- a label touches or covers its connector;
- two connectors share a segment or attach point;
- a connector passes behind a non-endpoint box;
- node text is clipped or too small at the intended size;
- the accent appears decorative rather than focal;
- a legend floats inside the content region;
- auto-layout erased the intended hierarchy.
