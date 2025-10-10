# React Router v7 Upgrade Complete

## Changes
- Migrated react-router-dom v6 → react-router v7
- Migrated @refinedev/react-router-v6 → @refinedev/react-router
- Updated Docker dev environment: Node 20 → Node 24 (react-router v7 requires >=20)
- Added engines field to package.json (node >=20.0.0)
- Fixed test mocks: react-router-dom → react-router

## Validation
- All 106 tests pass
- Dev/Prod Docker environments aligned (both Node 24)
