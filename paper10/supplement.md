# Supplement to The Intervention-Coverage Barrier

**Author:** Thomas Ryan  
**Status:** Public supplement; not peer reviewed  
**Version:** 1.0.0 - 29 August 2026

## S1. Scope

This supplement records the complete theorem assumptions, constructive fixtures, frozen analysis boundary, prior-art stress test, Paper 9 postmortem, research-program selection, controls, and reproducibility map. It is part of the Paper 10 audit package. The main manuscript controls the scientific claim.

The exact claim ceiling is:

> Finite successful functional tests do not by themselves certify uniform causal fidelity over a continuous intervention domain. A distributional statement needs an explicit intervention law and uncertainty design. A worst-case statement needs justified structure or sound regularity plus coverage.

The work does not show that a specific neural replacement is inadequate, that whole-brain emulation is impossible, or that consciousness, identity, survival, biological replaceability, or substrate independence is preserved or lost.

## S2. Definitions

Let $(X,\mathrm{dist})$ be the declared metric space of experimental conditions. A condition can encode initial state, finite intervention sequence, readout selection, environmental context, and horizon. The source and candidate induce interface trajectories $Y_S(x)$ and $Y_C(x)$. A declared nonnegative trajectory discrepancy $D$ gives

$$d(x) = D\!\left(Y_S(x),Y_C(x)\right).$$

For a finite nonempty battery $B$:

**Observed maximum:**

$$d_B=\max_{b\in B}\,d(b).$$

**Fill distance:**

$$\rho(B;X)=\sup_{x\in X}\,\min_{b\in B}\,\mathrm{dist}(x,b).$$

**Finite-battery pass at tolerance $\epsilon$:**

$$d_B\leq\epsilon.$$

**Distributional violation rate under law $P$:**

$$P\!\left[d(x)>\epsilon\right].$$

**Uniform pass:**

$$\sup_{x\in X}\,d(x)\leq\epsilon.$$

These are distinct estimands. No choice of terminology changes their logical relation.

## S3. Full proofs

### S3.1 Finite-set construction

**Theorem S1.** Let $X$ be a compact metric space, $B$ a finite proper subset of $X$, and $x_\star$ any point outside $B$. For every continuous source map $f_S:X\to\mathbb{R}^p$, nonzero vector $v\in\mathbb{R}^p$, and positive amplitude $a$, there exists a continuous candidate $f_C$ such that

$$f_C(b)=f_S(b)\quad(b\in B), \qquad \left\|f_C(x_\star)-f_S(x_\star)\right\|=a,$$

under the norm used to normalize $v$.

**Proof.** Define

$$r_B(x)=\min_{b\in B}\,\mathrm{dist}(x,b).$$

Each map $x\mapsto\mathrm{dist}(x,b)$ is 1-Lipschitz, and the pointwise minimum of finitely many 1-Lipschitz functions is 1-Lipschitz. Thus $r_B$ is continuous. Since $B$ is finite, it is closed. Since $x_\star$ is outside $B$, $r_B(x_\star)>0$. Normalize $v$ so $\left\|v\right\|=1$ and define

$$\phi(x) = a\frac{r_B(x)}{r_B(x_\star)}v.$$

For $b\in B$, $r_B(b)=0$, hence $\phi(b)=0$. At $x_\star$, $\left\|\phi(x_\star)\right\|=a$. Taking $f_C=f_S+\phi$ proves the claim. QED.

**Corollary S1.1.** Any algorithm that terminates after finitely many point queries cannot certify uniform equality over an unrestricted continuous class from query results alone.

**Reason.** Condition on the finite realized query set B. Theorem S1 supplies two continuous candidates consistent with all returned values but different elsewhere. Randomization or adaptivity changes the distribution of B, not its finiteness after termination.

### S3.2 Piecewise-linear and ReLU realization

Let $X$ be a compact rectangle in $\mathbb{R}^m$ with max-norm distance. For a fixed $b$,

$$\mathrm{dist}_\infty(x,b) = \max_i\,\left|x_i-b_i\right|.$$

Absolute value satisfies $|z|=\mathrm{ReLU}(z)+\mathrm{ReLU}(-z)$. Maximum and minimum satisfy

$$\max(a,b) = \mathrm{ReLU}(a-b)+b,$$

$$\min(a,b) = a-\mathrm{ReLU}(a-b).$$

Finite nesting therefore represents

$$\min_{b\in B}\,\max_i\,|x_i-b_i|$$

with a finite ReLU network. Scaling and adding the result to a ReLU-representable source preserves finite ReLU representability. This is an existence statement; it does not claim the representation is size-optimal or biologically plausible.

The compact cone used in the fixtures is

$$q_z(x) = A\,\mathrm{ReLU}\!\left(1-\frac{\left\|x-z\right\|_\infty}{r}\right).$$

It is zero outside the max-norm ball of radius $r$, equals $A$ at $z$, and has global Lipschitz constant $A/r$ under the max norm.

### S3.3 Tight fill-distance bound

**Theorem S2.** Let $d$ be $K$-Lipschitz on $X$. Then

$$\sup_X\,d \leq d_B + K\rho(B;X).$$

**Proof.** For arbitrary $x$ and any positive $\eta$, select $b\in B$ satisfying

$$\mathrm{dist}(x,b) \leq \min_{z\in B}\,\mathrm{dist}(x,z)+\eta.$$

Then

$$d(x) \leq d(b)+K\,\mathrm{dist}(x,b)$$

$$\leq d_B+K\min_{z\in B}\,\mathrm{dist}(x,z)+K\eta$$

$$\leq d_B+K\rho(B;X)+K\eta.$$

Let $\eta$ decrease to zero, then take the supremum over $x$. QED.

**Theorem S3 (tightness at zero observations).** For any nonempty $B$, define

$$d_\star(x)=K r_B(x).$$

This function is $K$-Lipschitz, vanishes on $B$, and satisfies

$$\sup_X\,d_\star=K\rho(B;X).$$

**Proof.** Distance to a set is 1-Lipschitz by the triangle inequality. Scaling supplies K-Lipschitz continuity. The other statements follow from the definitions of r and rho. QED.

For nonzero compatible observations, standard Lipschitz upper envelopes can give sharper point-specific bounds. The zero-observation witness is enough to prove that the residual term cannot be deleted from a general audit.

### S3.4 Unit-cube lower bound

**Theorem S4.** For $N$ points in $[0,1]^m$ under the max norm,

$$\rho \geq \frac{1}{2N^{1/m}}.$$

**Proof.** If $N$ closed max-norm balls of radius $r$ cover the unit cube, their intersections with the cube have total volume at most $N(2r)^m$. Coverage requires that total to be at least one. Thus $N(2r)^m\geq1$. Every covering radius, including the optimal radius, satisfies the stated inequality. QED.

If all tested discrepancies are zero and only a sound $K$-Lipschitz assumption is available, a certificate $K\rho\leq\epsilon$ therefore requires

$$N \geq \left(\frac{K}{2\epsilon}\right)^m.$$

Boundary clipping only decreases ball volume, so the inequality remains valid.

### S3.5 Recurrent error transport

Let source and candidate states be $s_t$ and $c_t$. Let $V$ be a nonnegative comparison function. Assume, for all paired states and inputs in a declared domain $R$,

$$V\!\left(F_S(s,u),F_C(c,u)\right) \leq L V(s,c)+\delta.$$

**Theorem S5.** If every paired state-input point reached through time T lies in R, then

$$V_t \leq L^tV_0+\delta\sum_{j=0}^{t-1}L^j$$

for $t\leq T$.

**Proof.** The case t=0 is immediate. Assume the result for t. Apply the one-step inequality:

$$V_{t+1} \leq L V_t+\delta$$

$$\leq L^{t+1}V_0+\delta\sum_{j=1}^{t}L^j+\delta$$

$$=L^{t+1}V_0+\delta\sum_{j=0}^{t}L^j.$$

Induction proves the result. QED.

For $L\neq1$, the sum is $(L^t-1)/(L-1)$; for $L=1$, it is $t$. If the output discrepancy satisfies

$$D_y\!\left(H_S(s),H_C(c)\right) \leq M V(s,c)+\delta_y,$$

then substitute the state bound. If the candidate leaves R, the proof stops at the exit time. A source-only trajectory tube is insufficient unless it is proved also to contain the candidate.

## S4. Constructive recurrent fixture

For each packet, the source is

$$s_{t+1}=a s_t+u_t, \qquad s_0=0.$$

The battery contains finite sequences sampled in $[-U,U]^T$. Over every battery sequence and time $t$, source state-input pairs are collected in

$$P_B=\left\{(s_t,u_t)\right\}.$$

A grid search chooses a center $z=(s_\star,u_\star)$ that maximizes the minimum of:

- its distance to every pair in $P_B$; and
- its distance from the lead-in path, so that input $s_\star$ reaches state $s_\star$ from zero without activating the bump.

The radius is 0.9 times this clearance. The candidate is

$$c_{t+1}=a c_t+u_t+q_z(c_t,u_t).$$

Every battery rollout remains identical because $q$ is zero at every visited pair. The unseen sequence begins with $u_0=s_\star$, then uses $u_1=u_\star$. The lead-in transition remains unchanged; the next transition activates the bump at its center and adds $A$. Thus the witness is dynamically reachable, not merely a point in an ambient state-input rectangle.

## S5. Exploratory and confirmatory separation

### S5.1 Exploratory freeze

The exploratory specification fixed:

- source recurrence and intervention bounds;
- 64 trajectories of horizon 8;
- a 0.20 bump;
- exact and causal tolerances;
- search-grid density;
- equal-budget coverage comparison;
- sham behavior; and
- gate conjunction.

Specification SHA-256:

`5fecc6bf14b1088f15c593fc8bf245fd3b2f33e0b1d6527c9066489ef94ce2d6`

### S5.2 Confirmatory freeze

The confirmatory specification was written after exploratory interpretation and before running `run_confirmatory.py`. It fixed five packets and forbade:

- packet deletion;
- seed replacement;
- threshold relaxation;
- search-grid expansion to rescue a failed witness; and
- pooled success in place of the conjunctive rule.

Specification SHA-256:

`4dcc507a26d1e67e7ad9bce0b6784ea4bc9319d056d921798ec9495da31a7050`

Runner SHA-256:

`0663d496d7104d28ad7bbe9b8a720b02b4e533dce87803f3ca37c52ead5eadfd`

The local hashes establish artifact identity only. They are not external timestamping and are not independent evidence.

## S6. Complete confirmatory packet results

| Packet | Trajectories | Tested pairs | Battery max | Unseen max | Approx. fill | Coverage upper bound | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| C01 | 32 | 192 | 0 | 0.12 | 0.127340 | 0.181099 | pass |
| C02 | 64 | 512 | 0 | 0.15 | 0.209941 | 0.620551 | pass |
| C03 | 96 | 960 | 0 | 0.18 | 0.223666 | 1.024686 | pass |
| C04 | 128 | 1,536 | 0 | 0.20 | 0.271177 | 2.039261 | pass |
| C05 | 48 | 432 | 0 | 0.14 | 0.127564 | 0.375507 | pass |

The primary rule required every packet to have tested discrepancy at most $10^{-12}$, unseen discrepancy at least 0.05, and a coverage upper bound above the 0.01 equivalence threshold. All five passed.

## S7. Coverage-design replications

| Seed | Budget | Regular fill | Median random fill | Ratio | Threshold | Result |
|---:|---:|---:|---:|---:|---:|---|
| 1732 | 49 | 0.083333 | 0.212136 | 0.392830 | 0.75 | pass |
| 2236 | 49 | 0.083333 | 0.217750 | 0.382702 | 0.75 | pass |
| 2645 | 49 | 0.083333 | 0.209800 | 0.397205 | 0.75 | pass |
| 3162 | 49 | 0.083333 | 0.208402 | 0.399869 | 0.75 | pass |
| 3741 | 49 | 0.083333 | 0.212208 | 0.392696 | 0.75 | pass |

Each random median used 50 batteries. All fill distances were evaluated on the same 101 by 101 grid. These are fixed deterministic computations and share code; they are not five independent scientific experiments.

## S8. Controls and failure semantics

| Control | Expected | Observed | Interpretation |
|---|---|---|---|
| exact replacement | zero interface error | 0 | execution path can reproduce identity |
| hidden unobservable mismatch | zero declared-interface error | 0 | interface scope is respected |
| unreachable mismatch | zero on declared experiment | 0 | reachability scope is respected |
| wrong interface offset | detected mismatch | 0.10 | measurement path has positive sensitivity |
| stable non-normal recurrence | transient amplification | 16.384x | local seams can amplify dynamically |
| linearly similar realizations | equal Markov sequence | max error $8.33\times10^{-17}$ | internal coordinates need not match |
| delayed linear mismatch | finite prefix match, later failure | first difference at index 8 | finite horizon cannot infer all horizons |

A failed coverage certificate means "insufficient evidence for the uniform claim," not "candidate known to fail." A found reachable witness means the constructed candidate actually fails at that intervention. The distinction is retained in every table and result JSON.

## S9. Hostile prior-art audit

### S9.1 Research streams checked

| Stream | Prior result or practice | Collision with a stronger Paper 10 claim | Surviving contribution |
|---|---|---|---|
| linear realization | finite Markov parameters can identify bounded-order minimal systems | kills a blanket claim that finite tests can never certify | assumptions must be stated; delayed sham shows horizon dependence |
| bisimulation/simulation | structural relations certify transition behavior | kills novelty of generic recurrence-transport theorems | candidate-inclusive domain obligation translated to neural replacement |
| symbolic reachability | explores or overapproximates entire state domains | kills novelty of using exhaustive verification after learning | contrast between sampled testing and verification |
| neural-network verification | certifies regional properties; broad cases are hard | kills novelty of generic "verify the network" proposal | claim ladder and fail-closed fidelity reporting |
| probabilistic verification | certifies under an explicit probability measure | kills novelty of distinguishing average and worst-case in general | forces intervention law into fidelity claims |
| Lipschitz optimization/optimal recovery | covering and minimax rates under regularity | kills novelty of the fill-distance inequality itself | operational audit and tight witness for functional-fidelity reports |
| WBE functional testing | proposes comprehensive standardized batteries | prior art for test-centered fidelity | identifies what a passed battery does and does not certify |
| controlled behavioral perturbation | held-out interventions, identifiability, domain bounds | prior art for perturbation richness and domain-relative reconstruction | explicit worst-case coverage/certificate rung |
| computational functionalism | complete future roles and intervention profiles | prior art for quantified functional organization | separates complete structure from finite evidence about it |
| consciousness falsification | substitution and prediction logic | adjacent prior art for falsification asymmetries | engineering-specific finite coverage barrier |

### S9.2 Priority statement

No exact primary source was found in the targeted 2024-2026 scan that operationalized the complete three-level audit - finite-battery falsification, intervention-law validation, and worst-case certification - for stateful neural replacement or whole-brain-emulation fidelity. This is a bounded search result, not proof of priority. The paper therefore claims a domain-specific synthesis and reporting framework, not invention of the underlying mathematics.

### S9.3 Rediscovery kill rule

If a prior source is found that contains the same three-level framework, recurrent candidate-inclusive condition, and operational fail-closed standard in this application, the novelty claim must be narrowed to independent replication or withdrawn before release.

## S10. Paper 9 postmortem

Paper 9 established a validated software path for substituting cell-type blocks inside a public connectome-constrained fly visual model. In two global checkpoints, all 45 locally eligible ladder cells preserved ordinary block responses and unchanged-decoder outputs within frozen 1% margins. Perturbation effects exposed a small Mi1 timescale gain deviation across two checkpoints and two integration steps. Effect-vector directions remained approximately collinear. A matched-local-error shunt control failed its eligibility/matching gate before confirmatory holdout exposure, so the mechanism-family interpretation was not confirmed.

Paper 9 explicitly did not establish:

- connectome sufficiency;
- biological neuron replaceability;
- a general local-to-global composition theorem;
- a family-specific causal mechanism effect;
- consciousness preservation;
- personal identity or survival; or
- substrate independence.

The attempted Paper 10 empirical extension recovered all 110 public recordings and the historical 156-coordinate loader shape, but only 154 neuron identifiers were common. On the frozen test split, reconstructed historical predictions reached aligned masked Pearson correlation 0.530543, NRMSE 1.056644, and mask coverage 0.840530. Train-test and connectome score deviations exceeded the frozen gates. The causal-compression direction was therefore killed before a new biological claim was made.

This failure shaped Paper 10 in two ways. First, it demonstrated that local hashes, tests, and recovered shapes do not rescue a failed scientific reconstruction. Second, it reinforced the difference between passing an available test set and possessing a certificate about the unobserved intervention domain.

## S11. Competing Paper 10 programs and decisions

Six programs were considered. Scores were ordinal, not measurements, and were used only to force explicit tradeoffs.

| Program | Novelty | Importance | Tractability | Meas. validity | Causal leverage | Repro. | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| Causal Compression Frontier in public worm dynamics | 4 | 5 | 3 | 3 | 5 | 4 | killed by frozen reconstruction gates |
| Matched-error causal seam in Paper 9 FlyVis model | 3 | 4 | 3 | 4 | 4 | 4 | no-go without eligible comparator |
| Finite Intervention-Basis theorem | 2 | 5 | 4 | 5 | 5 | 5 | killed by realization/verification prior art |
| Intervention-Coverage Barrier audit | 4 | 5 | 5 | 5 | 4 | 5 | selected with bounded novelty |
| Verification-aware reduced neural circuit benchmark | 4 | 4 | 2 | 5 | 5 | 4 | high-value follow-up; not needed for central theorem |
| Coverage-aware adaptive perturbation challenge | 4 | 4 | 3 | 4 | 4 | 5 | follow-up; requires hidden candidate suite |

The selected direction cleared the bar only after its claim was narrowed from a new positive basis theorem to a domain-specific audit framework grounded in credited mathematics. The alternative would have been a no-go, not novelty inflation.

## S12. Exact evidence ledger conventions

The project ledger labels every entry as one of:

- **Fact:** directly supported by an artifact, primary source, or executed result;
- **Inference:** a reasoned conclusion from facts with assumptions stated;
- **Speculation:** a plausible but untested possibility;
- **Proposal:** a future action, protocol, or design.

Hashes establish identity. Passing unit tests establishes behavior on the tested software paths. Multiple seeded packets establish deterministic transport across parameterizations. AI agreement establishes none of these independently.

## S13. Reproduction map

From the Paper 10 package root:

```text
python3 -m unittest discover -s work/g0d_intervention_coverage -p 'test_*.py' -v
python3 work/g0d_intervention_coverage/intervention_coverage.py
python3 work/g0d_intervention_coverage/run_confirmatory.py
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/paper10-mpl python3 paper10/build_artifacts.py
python3 paper10/verify_package.py
```

Re-running result generators overwrites deterministic result JSONs. The manifest and checksum verifier are the release audit. Confirmatory status depends on the preserved pre-execution specification and repository history; a rerun cannot create independent preregistration.

## S14. References unique to the supplement

Abate, A., Giacobbe, M., and Schnitzer, Y. (2024). Bisimulation Learning. https://doi.org/10.48550/arXiv.2405.15723

Cipresso, P. (2026). Measuring human behavior through controlled perturbations: a framework for reconstructing behavioral systems. https://doi.org/10.3389/fpsyg.2026.1833113

Froese, V., Grillo, M., and Skutella, M. (2025). Complexity of injectivity and verification of ReLU neural networks. https://proceedings.mlr.press/v291/froese25a.html

Geiger, A., et al. (2025). Causal abstraction: a theoretical foundation for mechanistic interpretability. https://www.jmlr.org/papers/v26/23-0058.html

Kanai, R., and Ma, S. (2026). Intrinsic computational functionalism and simulated consciousness. https://doi.org/10.48550/arXiv.2606.15348

Linssen, C., and Koene, R. (2025). Functional tests guide complex fidelity tradeoffs in whole-brain emulation. https://doi.org/10.55613/jeet.v35i1.152

Malherbe, C., and Vayatis, N. (2017). Global optimization of Lipschitz functions. https://proceedings.mlr.press/v70/malherbe17a.html
