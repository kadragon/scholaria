---
id: AG-LOADER-ROOT-001
version: 2.0.0
scope: global
status: active
supersedes: []
depends: []
last-updated: 2025-10-11
owner: team-admin
---
# Scholaria Agents Loader

> Root loader stub for modular agent knowledge. Follow the declared load sequence and respect local overrides.

## Load Order (Global)
1. `.agents/00-foundations/**`
2. `.agents/10-policies/**`
3. `.agents/20-workflows/**`
4. `.agents/30-roles/**`
5. `.agents/40-templates/**`
6. `.agents/90-overrides/**`

## Scope Tags
- Domain-specific directives now live within the shared folders above using `scope: folder:<name>` metadata.
- Introduce local loaders only if a component requires bespoke precedence rules.
