# Chronos V3 — The Architecture of Conjunctive Transparency

Reference architecture and implementation scaffold for the **Sovereign
Self-Correcting Cognitive System (SCCS)**: a bicameral reasoning
architecture in which a fast, stochastic hypothesis generator (System 1)
is never trusted on its own — every hypothesis it produces must pass
through a deterministic, cryptographically-signed verification stage
(System 2, the "Chronos Engine") before it can be treated as grounded, and
any case System 2 cannot decide alone is resolved by staked, consensus-based
arbitration (System 0).

We call the governing principle **Conjunctive Transparency (C-T)**: a
claim's content and the evidence for it travel together, signed,
hashable, and independently re-verifiable — never as an assertion with
evidence "available on request."

## Start here

**[`docs/architecture/00-overview.md`](docs/architecture/00-overview.md)**
is the entry point: repository map, the three subsystems, and reading
order for the rest of the architecture docs
([`01-bicameral-architecture.md`](docs/architecture/01-bicameral-architecture.md),
[`02-conjunctive-transparency.md`](docs/architecture/02-conjunctive-transparency.md),
[`03-posp-consensus.md`](docs/architecture/03-posp-consensus.md),
[`04-invariants.md`](docs/architecture/04-invariants.md)).

## Layout

```
proto/            gRPC service contracts for System 1, System 2, and System 0
db/migrations/     PostgreSQL schema: nodes, hypotheses, verifications, audit log, governance, PoSP consensus
libs/chronos_common/  shared primitives: canonical JSON (RFC 8785), Merkle hashing, Ed25519 signing, epistemic-state math
services/
  system1_hypothesis_generator/   System 1 reference service
  system2_chronos_verifier/       System 2 reference service (zero-hallucination lock)
  arbiter_module/                 System 0 reference service (PoSP consensus + L-E-J-D-A-S governance)
docker-compose.yml   local multi-service stack
Makefile             `make proto`, `make test`, `make up`, `make down`
```

## Running it locally

```sh
# 1. Generate gRPC stubs from proto/*.proto (requires grpcio-tools)
pip install grpcio-tools
make proto

# 2. Run each service's unit tests
make test

# 3. Bring up the full stack (Postgres, Redis, System 1/2/0)
make up
```

See [`SECURITY.md`](SECURITY.md) for the security policy.
