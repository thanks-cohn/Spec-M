# Spec-M RV64 / QEMU virt Reference Backend

This directory is reserved for the first RISC-V reference backend.

Target:

```text
architecture: RV64
platform: QEMU virt
initial profile: Spec-M Core
```

## Purpose

This backend should become the cleanest executable demonstration that Spec-M semantics can be realized naturally on RISC-V without importing x86 vocabulary.

It should eventually cover:

```text
privilege transition
SATP/address-space activation
ASID handling where enabled
SFENCE.VMA translation synchronization
trap entry/return
RVWMO-correct ordering
monotonic time and deadline timer
interrupt delivery
SBI services where appropriate
boot normalization from QEMU virt platform data
Virtio profile later
SMP profile later
```

## Rules

- Do not expose SATP, PLIC, SBI, or SFENCE.VMA to the portable kernel.
- Separate ISA-level code from QEMU-virt platform code where practical.
- Every implemented Spec-M transition should gain focused conformance evidence.
- Do not claim physical RISC-V hardware support from QEMU conformance alone.

## First implementation milestone

A useful first executable milestone is:

```text
boot under QEMU virt
    -> normalize boot state
    -> identify current CPU
    -> expose monotonic time
    -> exercise interrupt mask state
    -> execute deterministic Core conformance harness
```

Then proceed pressure-by-pressure toward address spaces, traps, userspace entry, SMP, and standard devices.
