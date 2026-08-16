# Diagram type routing

Select one dominant grammar. When the sibling `diagram-design` skill is present, read the listed reference before authoring.

| Showing | Type | Sibling reference |
|---|---|---|
| system components and connections | architecture | `type-architecture.md` |
| legacy landscape grouped by phase or department | IT current-state | `type-it-state.md` |
| decision logic and branches | flowchart | `type-flowchart.md` |
| messages ordered in time | sequence | `type-sequence.md` |
| states, transitions, and guards | state machine | `type-state.md` |
| entities, fields, and relationships | ER / data model | `type-er.md` |
| events positioned in time | timeline | `type-timeline.md` |
| cross-functional handoffs | swimlane | `type-swimlane.md` |
| two-axis positioning | quadrant | `type-quadrant.md` |
| entities scored across quantitative criteria | radar / spider | `type-radar.md` |
| reinforcing cycle | loop / flywheel | `type-loop.md` |
| hierarchy through containment | nested | `type-nested.md` |
| parent-to-child relationships | tree | `type-tree.md` |
| ownership, reporting, or escalation | org chart | `type-org-chart.md` |
| stacked abstraction levels | layer stack | `type-layers.md` |
| overlapping sets | Venn | `type-venn.md` |
| ranked hierarchy or conversion drop-off | pyramid / funnel | `type-pyramid.md` |
| category comparison | bar chart | `type-bar.md` |
| trends over time | line chart | `type-line.md` |
| tasks and phases over time | Gantt | `type-gantt.md` |
| distribution and correlation | scatter plot | `type-scatter.md` |
| end-to-end data stack | high-level | `type-high-level.md` |
| multi-actor sequential work | process | `type-process.md` |
| tiered data quality and access | medallion | `type-medallion.md` |
| role-scoped pipeline activity | data flow | `type-data-flow.md` |
| sources through platform to consumers | DP integration | `type-dp-integration.md` |
| role/component permissions | DP security matrix | `type-dp-security-matrix.md` |

## Draw.io-native grammar hints

- Architecture, flowchart, state, tree, org, process, and data-flow diagrams map naturally to nodes and orthogonal edges.
- Sequence diagrams use actor/header vertices, dashed lifeline edges without arrows, activation rectangles, and message edges. Do not use generic flowchart routing.
- Swimlanes use native `swimlane` containers; keep lane headers quiet and tasks aligned to a shared progression axis.
- ER diagrams use entity/table vertices and explicit crow's-foot edge endings. Keep fields inside their owning entity cell.
- Timeline and Gantt use a shared axis with native line and rectangle primitives; labels remain separate text cells.
- Radar, line, bar, scatter, Venn, quadrant, pyramid, and security-matrix diagrams use `primitives` rather than pretending every datum is a system node.
- Loop diagrams need a readable closed direction. Use explicit waypoints; never accept diagonal auto-routing around the ring.
- Nested and layer diagrams express containment primarily through placement. Remove connectors that merely repeat containment.

Do not hybridize grammars. If the content needs two grammars, create an overview page and a detail page.
