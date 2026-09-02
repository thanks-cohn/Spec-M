# Spec-M

**A standard machine substrate for kernels.**

> Define the smallest useful machine that a general-purpose kernel should be allowed to assume, then prove that real and virtual hardware can satisfy it.

Spec-M is an experiment in turning architecture portability into a machine-contract problem.

Instead of asking every kernel to understand every historical machine directly:

```text
kernel
  |
  +-> CR3 / SATP / TTBR
  +-> APIC / PLIC / GIC
  +-> HPET / TSC / SBI timers
  +-> UEFI / ACPI / Device Tree / firmware quirks
  +-> port I/O / MMIO / platform conventions
```

Spec-M asks a different question:

> **What machine-visible states and transitions does the kernel actually require?**

Then it defines those semantics once:

```text
                         KERNEL
                            |
                            v
                         SPEC-M
             canonical machine semantics
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
         x86-64            RV64           ARM64
            |               |               |
            v               v               v
        real/virtual     real/virtual    real/virtual
          hardware        hardware        hardware
```

The kernel speaks Spec-M.

The backend speaks the machine.

---

## The central idea

A kernel does not fundamentally need `CR3`.

It needs to make an address space active.

A kernel does not fundamentally need `INVLPG` or `SFENCE.VMA`.

It needs translation state to satisfy a defined visibility/invalidation rule.

A scheduler does not fundamentally need an x86 register frame or a RISC-V trap frame.

It needs execution state to be safely suspended and resumed.

Spec-M therefore standardizes **kernel-observable semantics**, not architecture vocabulary.

```text
x86-64                    Spec-M                    RV64
----------------------------------------------------------------
CR3 / PCID       ->   address-space state   <-   SATP / ASID
INVLPG/INVPCID   ->   translation sync      <-   SFENCE.VMA
APIC IPI         ->   CPU event delivery    <-   SBI/AIA/other
IRETQ/SYSRET     ->   user transition       <-   SRET
x86 TSO          ->   ordering contract     <-   RVWMO + fences
```

The physical implementations may be radically different.

The kernel-visible result must satisfy the same contract.

---

## What Spec-M is

Spec-M is intended to become four things at once:

1. **A state model** describing the machine state a portable kernel may rely on.
2. **A C contract** describing the operations that transform that state.
3. **A backend interface** for mapping real/virtual platforms onto those semantics.
4. **A conformance system** proving a backend actually satisfies the specification.

The important product is not the header file.

The product is:

```text
semantic state model
+ transition contracts
+ backend implementations
+ reproducible conformance evidence
```

---

## Relationship to Z-REF and X-REF

The projects have different jobs.

```text
Z-REF
    "What does a working kernel mechanism actually require?"

X-REF
    "How do we discover and migrate an existing kernel's machine assumptions?"

Spec-M
    "What is the canonical machine those kernels should target?"
```

Together:

```text
                    Z-REF
              executable reference
                     |
                     v
existing kernel -> X-REF -> Spec-M -> validated machine backend -> hardware
                     ^        |
                     |        +-> x86-64
                     |        +-> RV64
                     |        +-> ARM64 later
                     |        +-> virtual machine
                     |
              migration evidence
```

X-REF should increasingly port kernels **to Spec-M**, rather than performing one-off architecture-to-architecture rewrites.

Once a kernel cleanly targets Spec-M, adding another architecture should primarily become a backend problem.

---

## First-principles rule

**Spec-M contains a primitive only when a kernel requires the observable semantic property.**

It must not contain a primitive merely because one architecture has an instruction or device for it.

Bad Spec-M primitive:

```c
specm_write_cr3(...);
```

Good Spec-M primitive:

```c
specm_address_space_activate(...);
```

Bad:

```c
specm_apic_ipi(...);
```

Good:

```c
specm_cpu_signal(...);
```

Bad:

```c
specm_sfence_vma(...);
```

Good:

```c
specm_translation_sync(...);
```

If a proposed primitive would force ARM64 or RV64 to pretend to be x86, it is probably wrong.

---

## Spec-M state domains

The initial machine model is deliberately small.

### CPU

```text
CPU identity
online/offline state
execution context
privilege state
interrupt mask state
local machine capabilities
```

### Memory

```text
physical memory ranges
address spaces
virtual mappings
mapping permissions
translation visibility
data visibility / ordering
```

### Execution

```text
kernel context
userspace context
trap/exception state
entry/return transitions
```

### Interrupts and events

```text
pending event
masked/unmasked state
routing target
acknowledgement/completion
interprocessor signal
```

### Time

```text
monotonic time
programmed deadline
clock capabilities
```

### Multiprocessing

```text
CPU enumeration
CPU startup
CPU-local identity
cross-CPU signaling
shared-memory ordering
```

### I/O

```text
MMIO
DMA constraints
standard device discovery/profile
```

### Boot/lifecycle

```text
normalized boot manifest
memory map
CPU inventory
device inventory
initial console
shutdown
reboot
```

The specification should grow only under real kernel pressure.

---

## State transitions, not instruction equivalence

Spec-M should be modeled as a state machine.

For example:

```text
BEFORE
    cpu = 0
    privilege = supervisor
    address_space = A

transition:
    address_space.activate(B)

AFTER
    cpu = 0
    privilege = supervisor
    address_space = B
    stale translations cannot grant permissions from A
```

An x86 backend may satisfy this with CR3/PCID/invalidation rules.

An RV64 backend may satisfy it with SATP/ASID/SFENCE.VMA rules.

The backend is conforming when the **observable postconditions** hold.

This distinction is the foundation of Spec-M.

---

## Profiles

Not every machine needs every advanced feature.

Spec-M should use profiles rather than weakening core semantics.

Initial direction:

```text
Spec-M Core
    minimum machine required for a protected general-purpose kernel

Spec-M SMP
    multiple CPUs and interprocessor coordination

Spec-M Virtio
    standardized virtual devices

Spec-M PCIe
    standardized discoverable PCIe environment

Spec-M Hypervisor       future
    hardware virtualization primitives
```

A backend declares what it supports.

A kernel declares what it requires.

Missing required capabilities must fail explicitly rather than degrade silently.

---

## Devices: reuse standards where they are already good

Spec-M should not invent a new disk, network card, RNG, input protocol, or GPU interface merely to own every layer.

For virtual/generalized devices, **Virtio is the preferred starting point where appropriate**.

The first reference machine can therefore be intentionally boring:

```text
CPU
RAM
interrupt/event delivery
timer
console
virtio-blk
virtio-net
virtio-rng
virtio-input
virtio-gpu later
PCIe where useful
```

The innovation is the canonical kernel-machine boundary, not replacement of standards that already solve their layer well.

---

## Boot normalization

Real machines may begin through wildly different paths:

```text
UEFI
SBI
ACPI
Device Tree
Multiboot
custom firmware
```

The portable kernel should receive one normalized Spec-M boot manifest.

A backend owns the translation from firmware/platform representation into:

```text
memory regions
reserved regions
CPU inventory
kernel image information
initial console
device description
boot arguments
optional initrd
capabilities
```

The common kernel should not parse historical firmware formats unless it intentionally acts as a Spec-M backend.

---

## Conformance

A backend is not Spec-M compatible because its functions exist.

It is compatible because its observable behavior passes conformance.

```text
contract unit tests
        |
        v
backend state-transition tests
        |
        v
QEMU/platform tests
        |
        v
kernel integration tests
        |
        v
real workload pressure
```

Important negative tests must exist too:

```text
userspace cannot execute supervisor mappings
NX/non-executable mappings really fault
stale translations cannot bypass permission changes
CPU events are not silently lost
ordering contracts survive SMP stress
time does not move backward within its defined domain
```

See [`conformance/README.md`](conformance/README.md).

---

## Reference proving strategy

Spec-M should be derived empirically, not designed by committee in isolation.

The intended loop is:

```text
first-principles machine model
          |
          v
reference C contract
          |
          v
x86-64 backend + RV64 backend
          |
          v
Z-REF / real kernel pressure
          |
          v
Alpine / Python / browser / SMP / I/O pressure
          |
          v
X-REF ports unrelated kernel
          |
          v
missing abstraction discovered
          |
          v
refine Spec-M only when evidence demands it
```

If several independent kernels can target the same Spec-M contracts without architecture leakage, confidence in the model increases.

---

## Initial proving targets

The first reference backends should be:

```text
1. RV64 QEMU virt
2. x86-64 QEMU/PC-style reference backend
```

Then, once the semantics stabilize:

```text
3. one real RV64 board
4. one real x86-64 UEFI machine class
5. ARM64 reference backend
```

Real hardware support should be claimed only for explicitly tested/certified backend-platform combinations.

---

## Repository shape

```text
Spec-M/
├── README.md
├── include/
│   └── specm/
│       └── machine.h
├── spec/
│   └── STATE_MODEL.md
├── profiles/
│   └── core.yaml
├── backends/
│   └── README.md
├── conformance/
│   └── README.md
├── docs/
│   └── PRINCIPLES.md
└── agents/
    └── codex/
        └── PROMPT.md
```

This starts as a specification and reference framework. Code should grow around observed needs, not speculation.

---

## What success looks like

Spec-M becomes meaningful when we can demonstrate:

1. A working kernel targets Spec-M rather than architecture-specific primitives.
2. The same portable kernel core runs on x86-64 and RV64 Spec-M backends.
3. Backend conformance proves critical state transitions and protection invariants.
4. X-REF can migrate an unrelated x86 kernel onto Spec-M substantially faster than a direct architecture port.
5. That migrated kernel then inherits multiple validated Spec-M machine targets with little or no common-kernel change.
6. Each new kernel and backend improves the specification rather than creating another private HAL.

The long-term goal is simple:

> **Port the kernel to the standard machine once. Make the standard machine run everywhere.**

---

## One sentence

**Spec-M is the canonical kernel-visible machine: a small set of state, transitions, capabilities, and proofs that separate what kernels require from how hardware happens to provide it.**
