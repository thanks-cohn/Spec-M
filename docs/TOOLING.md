# Spec-M foundation tooling

Spec-M begins with executable tooling that is intentionally smaller than a hardware emulator.

The first goal is to make the **canonical machine semantics themselves inspectable and testable** before binding them to x86-64 or RV64 privileged machinery.

## Install

```sh
python -m pip install -e '.[test]'
```

## Commands

Validate the Core profile:

```sh
specm validate-profile profiles/core.yaml
```

Inspect the seeded semantic transition registry:

```sh
specm transitions
```

Exercise the deterministic model backend:

```sh
specm model-smoke
specm model-smoke --cpus 4
```

All command output is deterministic JSON suitable for agents, CI, and later conformance tooling.

## What the model backend is

`ModelMachine` is a semantic test double.

It models only enough state to ask questions such as:

```text
Did address-space activation change the active translation context?
Did translation synchronization advance the modeled visibility generation?
Can userspace entry occur without an active address space?
Does monotonic time move backward?
Does interrupt-mask state change explicitly?
```

It is deliberately not:

- an x86 emulator
- a RISC-V emulator
- a virtual machine
- a substitute for QEMU
- evidence that privileged hardware semantics are implemented

Its purpose is to make the specification executable before architecture backends exist.

## Why this matters

The intended proof ladder is:

```text
written transition contract
        |
        v
deterministic model behavior
        |
        v
architecture backend fixture
        |
        v
QEMU platform implementation
        |
        v
real kernel integration
        |
        v
real workload pressure
        |
        v
named real hardware
```

A transition should be understandable and testable at the top of that ladder before it is entangled with the bottom.

## Initial registry

The registry is seeded with a deliberately small set of transitions:

```text
SPECM-CPU-001   interrupt-mask-disable
SPECM-MM-001    address-space-activate
SPECM-MM-002    translation-sync
SPECM-TIME-001  monotonic-time-read
SPECM-EXEC-001  userspace-enter
```

These entries are seeds, not a frozen standard.

A new transition should be added only when real kernel or backend pressure demonstrates that the semantic property belongs in the canonical machine.

## Next causal milestone

The next useful implementation batch is:

1. Add tests for profile validation, registry stability, and model invariants.
2. Introduce a machine-readable backend manifest and conformance-claim validator.
3. Add a C model backend or C conformance harness that consumes `include/specm/machine.h`.
4. Define the first architecture backend boundary for RV64 without pretending QEMU-specific mechanisms are ISA semantics.
5. Implement the first RV64/QEMU-virt transition end-to-end, ideally monotonic time or early console/boot discovery before paging complexity.
6. Add negative tests that intentionally violate a contract and prove conformance catches them.

Do not jump from a Python model directly to claims of hardware compatibility.

The product is the chain of evidence.
