# Spec-M Codex Foundation Prompt

You are working inside **Spec-M**, a standard machine substrate for kernels.

Your job is not to invent a generic HAL full of architecture-shaped wrappers.

Your job is to help build the **smallest useful canonical machine model that a general-purpose kernel can target across architectures**.

Read first:

- `README.md`
- `docs/PRINCIPLES.md`
- `spec/STATE_MODEL.md`
- `profiles/core.yaml`
- `backends/README.md`
- `conformance/README.md`
- `include/specm/machine.h`

If X-REF is available beside this repository, inspect its machine-contract and porting documents as context. Spec-M is the canonical machine destination; X-REF is the migration system that moves existing kernels toward it.

## Central hypothesis

Kernel architecture ports repeatedly rediscover the same machine-level semantics through different historical mechanisms.

If we can define those semantics once as observable state and transitions, then:

```text
kernel -> Spec-M -> x86-64 backend
                 -> RV64 backend
                 -> ARM64 backend later
                 -> virtual machine backend
```

becomes preferable to repeated direct ports:

```text
kernel/x86 -> kernel/RV64
kernel/x86 -> kernel/ARM64
kernel/RV64 -> kernel/new-platform
```

The long-term objective is:

> **Port the kernel to the standard machine once. Make the standard machine run everywhere.**

## Prime directive

**Specify semantic state transitions, not instruction equivalents.**

Never add a portable primitive merely because an architecture exposes a convenient instruction, register, interrupt controller, firmware call, or historical facility.

Bad direction:

```text
write_cr3
send_apic_ipi
sfence_vma
load_ttbr
```

Good direction:

```text
address_space.activate
translation.sync
cpu.signal
userspace.enter
```

Before adding a primitive, identify:

```text
kernel requirement
observable precondition
observable postcondition
ordering requirement
privilege requirement
failure semantics
how at least two architectures can satisfy it naturally
how conformance can detect an incorrect implementation
```

## First milestone

Do not attempt real hardware breadth immediately.

Build the smallest executable foundation that allows Spec-M Core semantics to be tested independently of any full production kernel.

A strong first milestone is:

```text
1. stabilize the Core data model
2. create a small contract/transition registry
3. add machine-readable profile validation
4. add a minimal reference harness
5. create one fake/model backend used for deterministic tests
6. begin an RV64/QEMU-virt backend skeleton
7. create conformance fixtures for the first few transitions
```

Prioritize these initial semantic areas:

```text
machine discovery
CPU identity
interrupt mask state
monotonic time
memory ordering API
address-space activation model
translation synchronization model
context switching model
userspace-entry model
normalized boot manifest
```

Do not pretend a backend is complete where privileged runtime machinery does not yet exist.

## Required architecture discipline

Keep three things separate:

### 1. Spec-M semantic model

Architecture-neutral concepts only.

### 2. Architecture backend

Examples:

```text
x86-64 paging/privilege/traps/ordering
RV64 SATP/SFENCE/traps/RVWMO
```

### 3. Platform backend

Examples:

```text
QEMU virt boot/device description
SBI integration
APIC/PLIC/AIA/GIC instance
UEFI/ACPI/Device Tree normalization
board-specific reset/timer/console
```

Do not mistake a platform quirk for an ISA requirement.

## Conformance-first implementation

For each transition implemented, create evidence before moving on.

Desired pattern:

```text
semantic contract
    -> deterministic model test
        -> architecture fixture
            -> QEMU/platform test
                -> negative test
```

Whenever possible, add a mutation or intentionally broken variant demonstrating that the test actually catches a semantic violation.

Particularly important invariants:

```text
user/kernel isolation
execute protection
write protection
translation synchronization
memory ordering
monotonic time
context isolation
```

## Do not overdesign

Spec-M should grow from pressure.

Do not add networking, filesystems, schedulers, processes, syscalls, or application APIs. Those belong above the machine boundary.

Do not invent replacement device standards where Virtio/PCIe or another established standard is sufficient.

Do not introduce dozens of optional features merely because future hardware might have them.

A primitive must earn its place.

## Relationship with X-REF

Design Spec-M so X-REF can eventually transform this:

```text
foreign x86 kernel
    -> architecture-debt discovery
    -> semantic classification
    -> Spec-M boundary
    -> source x86 backend preserved
    -> RV64 Spec-M backend selected
```

This means Spec-M interfaces should be easy for an agent to map source-kernel behavior onto without encoding the source architecture.

Where X-REF and Spec-M overlap, Spec-M should own the normative machine semantics while X-REF may own richer migration metadata and heuristics.

## Relationship with Z-REF

Treat Z-REF as executable pressure and a source of proven kernel mechanisms, not as the sole authority for Spec-M design.

A useful Spec-M abstraction should survive:

```text
Z-REF implementation
another unrelated kernel
x86-64 backend
RV64 backend
future third architecture
```

If it only makes sense for one of those, inspect whether it is genuinely canonical.

## Success metric

Do not measure progress by number of APIs or generated files.

Measure:

```text
number of machine semantics precisely defined
number proved on two independent architectures/backends
number of real kernel assumptions that map cleanly to them
amount of backend-specific code prevented from leaking upward
amount of architecture-port work made reusable
```

The eventual experiment that matters is whether an unrelated kernel can be moved onto Spec-M through X-REF significantly faster than a traditional direct port, then run through more than one validated Spec-M backend.

## Working style

Work autonomously and incrementally.

For each batch:

```text
inspect current repository
identify smallest missing foundation
implement it
add tests
run tests
record evidence
avoid unsupported claims
identify next causal milestone
```

Keep code compact, explicit, and auditable.

When uncertain whether to add abstraction, prefer leaving the requirement documented and unresolved until a real kernel/backend pressure demonstrates the correct semantic boundary.

## Final principle

The elegance of Spec-M should come from reduction:

```text
many machines
    -> few kernel-visible states
        -> few explicit transitions
            -> many backend implementations
```

Build the machine that kernels should have been able to target all along.
