# Spec-M x86-64 Reference Virtual-PC Backend

This directory is reserved for the first x86-64 reference backend.

Target:

```text
architecture: x86-64
platform: reproducible QEMU/PC-style reference environment
initial profile: Spec-M Core
```

## Purpose

The x86-64 backend is not merely compatibility support. It is a second independent realization of the same Spec-M semantics and an important defense against accidentally designing the specification around RISC-V.

It should eventually cover:

```text
privilege transition
CR3/address-space activation
PCID handling where enabled
translation invalidation
trap/interrupt entry and return
x86 memory-order realization of Spec-M ordering
monotonic time and deadline timer
interrupt routing/signaling
boot normalization from the chosen reference environment
Virtio profile later
SMP profile later
```

## Rules

- Do not expose CR3, APIC, GDT, IDT, TSS, MSRs, or INVLPG to the portable kernel.
- Prefer a clean reproducible reference environment over exhaustive legacy-PC emulation.
- Preserve strong x86 behavior only where Spec-M promises it. Do not accidentally make x86 TSO the portable specification.
- Every implemented transition should have conformance evidence shared conceptually with the RV64 backend.

## First implementation milestone

```text
boot reference machine
    -> normalize boot state
    -> identify current CPU
    -> expose monotonic time
    -> exercise interrupt mask state
    -> execute deterministic Core conformance harness
```

The x86 and RV64 reference backends should increasingly run the same normalized semantic tests.
