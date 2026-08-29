# Paper 10 Release Notes

## Release

Tag: `paper10-v1.0.0`

Title: Paper 10 preprint v1.0.0 - The Intervention-Coverage Barrier

## Paper

**The Intervention-Coverage Barrier: Why Finite Functional Tests Cannot Certify Neural Replacement Fidelity**

Zenodo DOI: [10.5281/zenodo.22166381](https://doi.org/10.5281/zenodo.22166381)

This release packages the Paper 10 methods and theory preprint, proof supplement, frozen specifications, deterministic construction and controls, result JSONs, figures, tables, exact evidence ledger, and reproducibility audits.

## Core contribution

Paper 10 establishes an intervention-coverage barrier for functional-fidelity claims. It separates a passed finite battery from distributional validation under an explicit intervention law and from worst-case certification under sound structural or regularity-and-coverage assumptions.

The release distinguishes three different claims: finite-battery falsification, distributional validation under an explicit intervention law, and worst-case certification under justified structural or regularity-and-coverage assumptions. It gives a constructive recurrent counterexample and a fail-closed coverage audit.

## Included artifacts

- full manuscript and proof supplement;
- five figures and machine-readable tables;
- frozen exploratory and confirmatory specifications;
- deterministic recurrent construction and controls;
- five conjunctive confirmatory packets;
- unit tests, PDF renderer, integrity verifier, and checksums;
- Papers 1-9 lineage and Paper 9 postmortem;
- exact evidence ledger with fact/inference/speculation/proposal labels; and
- sole-human-authorship and AI-assistance disclosure.

## Frozen fixture result

All five frozen packets passed without amendment. Across 368 trajectories and 3,632 tested state-input pairs, tested discrepancy was exactly zero. Reachable unseen discrepancies were 0.12-0.20. All sound constructed coverage bounds exceeded the 0.01 uniform threshold and therefore failed closed. All five equal-budget coverage-design replications also passed.

## Claim boundary

The analytic proof supports the general finite-set statement. Repeated seeded fixtures only test implementation transport. The paper does not establish consciousness preservation, emulation impossibility, or failure of any specific replacement.

## Integrity

Run `python3 paper10/verify_package.py` from the repository root to verify frozen hashes, result totals, claim markers, figures, tables, PDFs, and the release manifest. Local hashes, deterministic reruns, passing tests, and AI agreement are non-independent process evidence.

## Authorship and license

Thomas Ryan is the sole human author and accountable operator. AI systems assisted but are not authors or independent validators. Paper text, tables, original figures, and included code are released under CC BY 4.0 unless a file states otherwise.
