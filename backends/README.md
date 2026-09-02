# Spec-M Backends

A Spec-M backend maps one real or virtual machine environment onto the canonical Spec-M state model.

A backend is not an architecture port of a kernel.

It is the machine-side implementation of the contract that allows many kernels to target the same abstract machine.

## Backend boundary

```text
portable kernel
      |
      v
Spec-M contract
      |
      v
backend
      |
      +-> ISA mechanisms
      +-> firmware services
      +-> interrupt controller
      +-> timer source
      +-> boot discovery
      +-> platform quirks
      +-> standard devices/profiles
      |
      v
real or virtual machine
```

The portable kernel should not need to know whether the backend uses:

```text
CR3 or SATP
APIC or PLIC/AIA or GIC
UEFI or SBI
ACPI or Device Tree
port I/O or MMIO
```

unless that information is intentionally exposed by a higher optional profile.

## Architecture backend vs platform backend

Spec-M distinguishes two layers of machine specificity.

### Architecture semantics

Examples:

```text
privilege transition
address-space activation
translation synchronization
atomic ordering
trap state
context state
```

These belong primarily to an ISA/privileged-architecture implementation.

### Platform semantics

Examples:

```text
boot entry
memory discovery
interrupt-controller instance
CPU startup mechanism
timer wiring
UART/console
PCIe root complex
device enumeration
reset/power control
```

These depend on the machine/platform.

A clean backend should avoid mixing them unnecessarily.

Suggested structure:

```text
backends/
├── x86_64/
│   ├── arch/
│   └── platforms/
│       └── qemu-pc/
├── riscv64/
│   ├── arch/
│   └── platforms/
│       └── qemu-virt/
└── arm64/                  future
```

## Initial reference targets

The first backend pair should optimize for clarity and reproducibility rather than hardware breadth.

### RV64 / QEMU virt

Use this to prove:

```text
RISC-V privilege mapping
SATP/address-space state
SFENCE.VMA translation semantics
RVWMO ordering
trap/user transitions
SBI/platform services where appropriate
QEMU virt interrupt/timer/device environment
```

### x86-64 / reference virtual PC

Use this to prove that the same Spec-M contracts can be satisfied naturally by a significantly different architecture.

The goal is not exhaustive legacy PC compatibility.

The goal is a clean reference backend that gives X-REF and Z-REF a second independent implementation of the same machine semantics.

## Real hardware certification

A backend should never claim `riscv64 hardware support` as one undifferentiated fact.

Real-hardware claims name the actual supported platform/profile combination.

Example:

```text
architecture: riscv64
platform: qemu-virt
Spec-M Core: PASS
Spec-M SMP: PASS
Spec-M Virtio: PASS

architecture: riscv64
platform: example-board-revA
Spec-M Core: PASS
Spec-M SMP: PARTIAL
Spec-M Virtio: N/A
```

This keeps architecture truth separate from board truth.

## Backend implementation rule

The backend should choose the target machine's **native natural mechanism** for each Spec-M state transition.

Do not preserve the source implementation shape merely because X-REF discovered it in an old kernel.

For example:

```text
Spec-M:
    address_space.activate

x86-64:
    CR3/PCID logic as appropriate

RV64:
    SATP/ASID logic as appropriate
```

The common contract is the point of equivalence.

## Private backend helpers

Backends may contain arbitrary private helpers.

Examples:

```text
x86_load_gdt()
riscv_sbi_hart_start()
qemu_virt_parse_dtb()
x86_apic_init()
```

They must not become portable-kernel dependencies unless their semantic purpose is first promoted into the Spec-M model.

## Conformance obligation

Every backend PR should answer:

```text
Which Spec-M transition/invariant does this implement?
Which architecture/platform mechanism realizes it?
What preconditions are assumed?
What observable postconditions are proved?
What negative test would detect a broken implementation?
What exact machine/platform was tested?
```

A backend with code but no evidence is incomplete.
