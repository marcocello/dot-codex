# Builder specification

`build_drawio.py` accepts UTF-8 JSON and emits uncompressed Draw.io XML.

## Top level

```json
{
  "title": "Request path",
  "description": "Architecture showing a browser calling an API that writes to a database.",
  "type": "architecture",
  "audience": "mixed",
  "detail": "balanced",
  "page": {"name": "Overview", "width": 1200, "height": 720, "background": "#f5f5f5"},
  "header": {"eyebrow": "SYSTEM MAP", "title": "Request path", "subtitle": "A deliberately small operational view"},
  "zones": [],
  "edges": [],
  "edge_labels": [],
  "nodes": [],
  "primitives": [],
  "legend": []
}
```

Required: `title`, `description`, `page`, and at least one `node` or `primitive`.

## Nodes

```json
{
  "id": "api",
  "kind": "focal",
  "x": 480,
  "y": 240,
  "w": 160,
  "h": 80,
  "tag": "API",
  "label": "Orders API",
  "sublabel": "https :443",
  "shape": "rect"
}
```

Supported `kind`: `focal`, `backend`, `store`, `external`, `input`, `optional`, `security`, `decision`, `state`, and `plain`.

Supported `shape`: `rect`, `ellipse`, `rhombus`, `cylinder`, `cloud`, `hexagon`, `triangle`, and `parallelogram`. A `store` defaults to `cylinder`; a `decision` defaults to `rhombus`; all others default to `rect`.

Optional `style` appends native Draw.io style tokens. Use it sparingly.

## Zones

```json
{"id": "private", "x": 432, "y": 176, "w": 496, "h": 240, "label": "PRIVATE SERVICES"}
```

Zones render before connectors and nodes. Keep at most three for architecture diagrams.

## Edges

```json
{
  "id": "request",
  "source": "web",
  "target": "api",
  "kind": "link",
  "label": "HTTPS",
  "source_port": {"x": 1, "y": 0.4},
  "target_port": {"x": 0, "y": 0.4},
  "waypoints": [{"x": 360, "y": 248}]
}
```

Supported edge `kind`: `default`, `accent`, `link`, `optional`, `async`, `return`, and `passive`.

Ports are normalized to a node edge: `x=0` left, `x=1` right, `y=0` top, `y=1` bottom. Specify both ports. Fan repeated edge attachments; never reuse the same `(x,y)` on the same node.

Keep `label` on the edge for semantics, but render it using a separate entry in `edge_labels`:

```json
{"id": "request-label", "edge": "request", "x": 320, "y": 216, "w": 64, "h": 16, "text": "HTTPS"}
```

The label box must remain 6–10 px clear of the connector. The builder cannot infer that visual relationship; inspect the preview.

## Primitives

Use primitives for chart axes, bars, bands, lifelines, activation blocks, matrix cells, annotations, and other native Draw.io geometry.

```json
{
  "id": "baseline",
  "x": 160,
  "y": 520,
  "w": 720,
  "h": 0,
  "value": "",
  "style": "shape=line;strokeColor=#bfc0c0;strokeWidth=1;"
}
```

Every primitive requires `id`, `x`, `y`, `w`, `h`, and `style`. Optional `value` supports escaped HTML labels.

## Legend

```json
[
  {"kind": "focal", "label": "Primary service"},
  {"kind": "link", "label": "External/API flow"}
]
```

The builder positions the legend in one horizontal strip near the bottom of the page. Increase page height if the content would collide with it.

## Grid and bounds

- Use integer coordinates and dimensions divisible by 4.
- Keep content within the declared page.
- Set explicit page dimensions for the intended output; use `assets/example-architecture.json` as the default 1200 × 720 reference.
- The builder rejects duplicate IDs, unknown endpoints, repeated attachment points, built-in edge labels without label cells, over-budget content, and non-grid geometry.
