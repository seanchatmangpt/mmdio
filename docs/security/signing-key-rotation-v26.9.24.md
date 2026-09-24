# Signing-key rotation (v26.9.24)

Recorded 2026-09-24 (fleet key scan after the single-repo migration). Base `e7c816550364` of `mmdio`.
Every private key listed here was committed to this repository and is therefore compromised: every receipt or
attestation signed with it carries no signing authority (standing REFUSED, broken_term R_missing_authority).
The keys leave the tree (history is not rewritten; no force-push), and each key directory's `.gitignore` now
covers both halves. Every checkout keeps its own pair: ggen generates one on first use, and a tracked public
half without its private half would make that first `ggen sync` refuse [FM-KEY-010/011]. The canonical
checkout's new public key is published below for anyone verifying its future receipts.

| key dir | removed private key sha256 | removed public key sha256 | new public key (canonical checkout) |
|---|---|---|---|
| `.ggen/keys` | `46fe861dfb782464f57f59f29a51268b7bce4268977f7fd6c071aef242159e71` | `00eaaf6be6fa2eb5b43448673b5a6808c436d0f751da8d56bdb727da471a5a56` | `238c34e7da2f8043997712e513af0861aeff59cc0a00ca0013accd69abd081ff` |
