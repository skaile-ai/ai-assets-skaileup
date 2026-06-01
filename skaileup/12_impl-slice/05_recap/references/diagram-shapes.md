# Diagram starter shapes

Five starter ASCII shapes — one per `diagram_type` enum value. Use these as
templates: rename the nodes to match this slice; add branches/error paths
where relevant; remove unused boxes. NEVER copy verbatim — a customised
diagram is the whole point.

The validator pins three structural traits, regardless of which shape you
pick: a fenced code block (no language identifier), ≥ 5 non-empty lines,
and at least one of the diagram characters `→ > | ─ +`.

## 1. data-flow (default)

```
+----------+      submit       +-----------+      writes      +---------+
|  <UI>    | ----------------> | <handler> | ---------------> | <data>  |
|  screen  | <---------------- |  fn/route | <--------------- |  table/ |
+----------+   re-render w/    +-----------+   row-back       |  store  |
              fresh data                                       +---------+
```

## 2. control-flow

```
            +-----------------+
            |  user clicks N  |
            +--------+--------+
                     |
                     v
           +---------+---------+
           |   valid input?    |
           +----+----------+---+
              yes |        | no
                  v        v
         +--------+--+  +--+--------+
         |  persist  |  |  show err |
         +--------+--+  +-----------+
                  |
                  v
           +------+------+
           |   re-render |
           +-------------+
```

## 3. component-tree

```
<App>
└── <RouteX>
    └── <FeatureScreen>
        ├── <Header />
        ├── <List>
        │   └── <Item />     (× N)
        └── <Composer>
            ├── <Input />
            └── <SubmitBtn />
```

## 4. state-machine

```
   [idle] --open--> [composing]
                       |
                       +--submit--> [pending]
                       +--cancel--> [idle]
   [pending] --ok--> [success] --reset--> [idle]
   [pending] --err--> [error]   --retry--> [pending]
```

## 5. request-lifecycle

```
 t=0ms  Client  ──── POST /comments ────►  Edge  ──► Handler
 t=12ms                                                │
                                                       v
 t=24ms                                            DB INSERT
                                                       │
                                                       v
 t=40ms                                            Pusher.broadcast
 t=55ms ◄──── 201 + JSON ──── Edge ◄────────── Handler
 t=72ms ◄──── ws message ──── Pusher
```

## Customisation rules

- Rename nodes to this slice's actors. "<UI>" is a placeholder; replace it.
- Add error paths if the slice has explicit failure modes.
- Add branches at decision points. A linear flow is a smell — most slices
  have at least one yes/no.
- Remove unused boxes. A 7-node starter shape is rarely the right size.
- Soft note on portability: `→` may strip in some markdown viewers. Prefer
  `>` (e.g. `--->`, `<---`) if your downstream renderers strip Unicode.
  The validator accepts either.
