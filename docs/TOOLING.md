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

Validate a backend declaration and its evidence-bounded claim:

```sh
specm validate-backend backends/riscv64/qemu-virt/manifest.yaml
specm conformance backends/riscv64/qemu-virt/manifest.yaml
```

Exercise the deterministic model backend:

```sh
specm model-smoke
specm model-smoke --cpus 4
```

All command output is deterministic JSON suitable for agents, CI, and later conformance tooling.

## Executable in this milestone

- The transition registry carries inputs, outputs, preconditions,
  postconditions, ordering, privilege, failure behavior, invariants, and
  capability requirements. Missing fields and duplicate identities fail.
- Backend manifests keep architecture and platform identities separate and are
  checked against the Core profile, known transitions, and cumulative evidence
  requirements.
- The model exercises per-CPU interrupt/privilege/address-space state, stale
  translation visibility, mapping permissions, monotonic time, one-shot
  deadlines, CPU signals, ordering records, and normalized boot facts. Negative
  fixtures prove rejection of unsafe userspace entry, clock regression,
  unsynchronized permission assumptions, and unsupported conformance claims.
- The RV64 architecture layer contains one real, cross-compilable `rdtime`
  boundary. It returns raw architectural ticks only; it is not presented as a
  completed platform clock.

## Evidence and forbidden claims

The deterministic Python suite establishes model/unit evidence for the tooling,
not for either seeded machine backend. Both backend manifests therefore claim
only C0_SPECIFIED. No QEMU boot, kernel integration, workload, or physical-board
claim is established. In particular, a successful cross-compile is not C3
architecture conformance and QEMU evidence could never establish C7 hardware.

## Next causal backend blocker

The next bounded step is a freestanding RV64 QEMU-virt payload which normalizes
firmware-provided `timebase-frequency`, converts `rdtime` ticks into a declared
Spec-M time unit, emits a deterministic monotonic trace, and runs with pinned
QEMU/OpenSBI versions. This platform normalization must precede a truthful C4
monotonic-time claim; timer interrupts, paging, and userspace should not be
stubbed ahead of it.

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
SPECM-CPU-002   cpu-signal
SPECM-TIME-002  deadline-set
SPECM-MEM-003   memory-fence
```

These entries are seeds, not a frozen standard.

A new transition should be added only when real kernel or backend pressure demonstrates that the semantic property belongs in the canonical machine.

Do not jump from a Python model directly to claims of hardware compatibility.

The product is the chain of evidence.
