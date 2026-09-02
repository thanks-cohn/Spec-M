# Spec-M Transition Contract Template

Every normative Spec-M transition should be describable with this record.

The purpose is to keep prose, C interfaces, backend implementation, and conformance evidence tied to the same semantic object.

```text
id:
name:
state_domains:
profile:
status:

intent:

inputs:
outputs:

preconditions:

transition:

postconditions:

ordering:

privilege:

failure_semantics:

observable_behavior:

forbidden_behavior:

source_pressures:
    kernels/workloads that demonstrated the need

reference_realizations:
    x86-64:
    RV64:
    future-third-architecture:

conformance:
    positive:
    negative:
    stress:
    differential:

known_non_equivalences:

open_questions:
```

## Example skeleton

```text
id: SPECM-MM-001
name: address-space-activate
state_domains:
    - cpu
    - address-space
    - translation
profile: Spec-M Core
status: DRAFT

intent:
    Make address space B the current translation/protection domain for the
    calling CPU.

preconditions:
    - B is valid for the backend.
    - required kernel mappings are available under the backend/kernel model.
    - caller has required privilege.

postconditions:
    - subsequent portable-kernel-visible translations use B.
    - permissions observed through those translations agree with B.
    - stale translations cannot preserve access forbidden by B after required
      synchronization semantics are complete.

ordering:
    Backend must perform any ordering required before the postconditions can be
    relied upon by subsequent execution.

reference_realizations:
    x86-64:
        CR3/PCID/invalidation strategy as appropriate.
    RV64:
        SATP/ASID/SFENCE.VMA strategy as appropriate.

conformance:
    positive:
        Switch between A and B where the same VA maps different backing pages.
    negative:
        Ensure stale permissions cannot survive transition/synchronization.
```

## Acceptance test for a new contract

Before a contract becomes normative, reviewers should be able to answer yes to:

1. Does this describe a kernel requirement rather than one architecture's mechanism?
2. Can at least two meaningfully different architectures implement it naturally?
3. Are the observable postconditions precise enough to test?
4. Are security/protection consequences explicit?
5. Is ordering explicit where relevant?
6. Is the primitive smaller and clearer than leaking the backend mechanism upward?
7. Has real implementation or kernel pressure demonstrated the need?

If not, keep it experimental.
