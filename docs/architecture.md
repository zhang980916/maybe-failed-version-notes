# Architecture

The lab is split into four deliberately small layers.

## Registry

The registry layer records factor metadata and experiment manifests. It does not make trading decisions. In a private deployment, this layer can point at a local data lake through `ASRL_DATA_DIR`; in this public-safe draft it uses mock files.

## Gladiator

The Gladiator layer ranks factor combinations. The demo implementation uses a transparent score:

```text
mean_ic_20d + category_diversity_bonus - concentration_penalty
```

This is intentionally simple so the repository can be reviewed safely. A private deployment can replace the scoring backend with real walk-forward metrics.

## Dashboard Bridge

The bridge turns registry outputs, candidate files, and experiment records into one JSON payload for the static dashboard.

## Dashboard

The dashboard is read-only. It has no order placement, broker integration, credential access, or live message sending.
