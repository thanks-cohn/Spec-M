# Codex Request: Build the First Executable Spec-M Foundation

You are continuing the initial implementation of **Spec-M**, the canonical kernel-visible machine specification.

Read first:

- `README.md`
- `agents/codex/PROMPT.md`
- `docs/PRINCIPLES.md`
- `docs/TOOLING.md`
- `spec/STATE_MODEL.md`
- `spec/CONTRACT_TEMPLATE.md`
- `profiles/core.yaml`
- `include/specm/machine.h`
- `backends/README.md`
- `conformance/README.md`
- all current files under `src/specm/` and `tests/`

If the sibling X-REF repository is available, inspect its machine-contract and tooling model for interoperability context, but do not copy X-REF migration concepts into the Spec-M normative machine layer.

## Objective

Build the smallest coherent executable foundation that makes this statement increasingly true:

> A kernel targets one small, stable machine contract. Independent x86-64, RV64, and future machine backends prove they provide the same kernel-visible semantics.

The immediate milestone is **not** to boot a production kernel.

The immediate milestone is to make the Spec-M Core specification sufficiently executable that an architecture backend can be implemented against explicit, machine-readable, testable requirements.

## Existing foundation

The repository already contains:

- a draft normative machine state model
- a C machine contract
- a Core profile
- conformance philosophy
- backend separation rules
- a Python tooling package
- profile validation
- a semantic transition registry
- a deterministic model backend
- initial model/profile tests

Preserve these ideas unless evidence demonstrates a better boundary.

## Implement this batch

### 1. Strengthen the transition registry

Make the transition registry a real machine-readable contract source.

Each transition should be able to represent at minimum:

```text
id
name
domain
intent
inputs/outputs where applicable
preconditions
postconditions
ordering requirements
privilege requirements
failure semantics
normative invariants
capabilities required
```

Validate uniqueness and required fields.

Do not encode CR3, SATP, APIC, PLIC, GIC, SBI call numbers, or architecture instructions into normative transition identities.

### 2. Add backend manifests

Create a machine-readable backend manifest format that separates:

```text
architecture backend
platform backend
supported Spec-M profiles
supported capabilities
implemented transitions
conformance level
evidence artifacts
known non-equivalences / limitations
```

Seed draft manifests for:

```text
RV64 / QEMU virt
x86-64 / QEMU PC/reference
```

These are declarations, not proof. Validation must reject claims that exceed recorded evidence.

### 3. Build conformance claim validation

Implement deterministic validation for the C0-C7 conformance ladder described in `conformance/README.md`.

A backend must not be able to claim:

```text
C3 architecture conformance without architecture evidence
C4 platform conformance without platform evidence
C5 kernel integration without kernel evidence
C6 workload conformance without workload evidence
C7 real-hardware conformance without named hardware evidence
```

Compilation alone must never upgrade conformance.

### 4. Expand the deterministic model backend

Extend the model only enough to exercise Core semantics.

Priorities:

```text
interrupt mask state
address-space activation
translation synchronization
mapping permissions/protection model
monotonic time
one-shot deadline state
CPU identity
multi-CPU state representation
CPU signaling model
userspace privilege transition
memory-order contract representation
normalized boot manifest representation
```

Do not turn it into an ISA emulator.

### 5. Add negative conformance tests

For every important invariant added, include at least one deliberately invalid case where practical.

Examples:

```text
userspace entry without an active address space -> fail
monotonic clock regression -> fail
backend claiming C7 without named hardware evidence -> fail
duplicate transition IDs -> fail
profile requiring unsupported capability -> fail
translation synchronization omitted after invalidating permissions -> detectable failure in model fixture
```

The verifier must prove it can reject bad states, not merely accept good fixtures.

### 6. Establish the first RV64 backend boundary

Create the initial source/layout skeleton for:

```text
backends/riscv64/
backends/riscv64/qemu-virt/
```

Clearly separate:

```text
RV64 ISA semantics
    SATP / privilege / trap / ordering implementation details

QEMU-virt platform semantics
    firmware discovery / SBI integration / interrupt-controller instance /
    timer wiring / UART / device description
```

Do not implement a large amount of privileged code merely to make progress look impressive.

A correct skeleton plus one tiny end-to-end backend capability is better than many unproved stubs.

Preferred first executable backend pressure, choose the smallest tractable one:

```text
machine/CPU discovery
monotonic time
normalized early boot information
early console
```

Explain why you chose it.

### 7. Add CLI surfaces

Keep CLI output deterministic JSON.

Useful commands may include:

```text
specm validate-profile profiles/core.yaml
specm transitions
specm validate-backend <manifest>
specm conformance <manifest>
specm model-smoke
```

Do not add commands whose output implies hardware support that has not been demonstrated.

### 8. Document the next causal milestone

At the end of the batch, update `docs/TOOLING.md` with:

```text
what became executable
what remains only specified
what evidence passes
what claims are forbidden
next first causal backend blocker
```

## Architectural rule

The key question for every API is:

> Is this something a general-purpose kernel fundamentally needs to observe or cause, or is it merely how one particular architecture/platform implements that need?

If it is the latter, keep it below Spec-M Core.

## Success criteria for this request

This batch is successful when:

1. `pytest` passes.
2. Core profile validation is deterministic.
3. Transition registry validation is deterministic.
4. Backend manifest validation exists.
5. Conformance claims cannot outrun evidence.
6. The model backend has meaningful positive and negative tests.
7. RV64 architecture and QEMU-virt platform boundaries exist clearly in source/docs.
8. No code claims real hardware compatibility.
9. The next backend pressure is explicit and bounded.

## Long-term context

Spec-M should eventually make this possible:

```text
SerenityOS-like x86 kernel
        |
        v
      X-REF
        |
        v
      Spec-M
        |
        +----> x86-64 backend
        +----> RV64 backend
        +----> ARM64 backend
        |
        v
same portable kernel core
```

The purpose of this request is to build the first trustworthy inch of that bridge.

Do not optimize for file count.
Do not optimize for demo theater.
Optimize for **small semantics, strong evidence, and reusable portability**.
