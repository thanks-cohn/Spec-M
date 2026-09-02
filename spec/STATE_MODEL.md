# Spec-M Canonical State Model

Spec-M models the machine as a set of **kernel-observable state domains** plus **legal state transitions**.

The specification does not require backend internals to resemble this model. It requires the backend to preserve the model's observable semantics.

## 1. CPU state

Each CPU has at least:

```text
identity
online/offline state
current privilege domain
current execution context
interrupt-enabled state
current address-space association
local capability state
```

A backend may have additional architectural state. That state is private unless the portable kernel must observe it.

### Required transitions

```text
cpu.start
cpu.halt
cpu.relax
cpu.signal
context.switch
userspace.enter
interrupt.enable
interrupt.disable
```

## 2. Address-space state

The machine exposes the concept of an active address space.

A Spec-M address space is not a CR3 value, SATP value, TTBR value, or raw page-table format.

It is a kernel-owned identity for a translation/protection domain.

### Required invariant

After successful activation of address space `B`:

```text
- translations used for portable-kernel-visible accesses obey B
- permissions are those established for B
- stale translation state cannot preserve access that B forbids
- required kernel mappings remain valid according to the kernel/backend contract
```

### Required transitions

```text
address_space.activate
typical mapping changes occur through kernel VM/backend integration
translation.sync(address)
translation.sync(address_space)
translation.sync(global)
```

## 3. Mapping/protection state

The portable semantic permission set begins with:

```text
READ
WRITE
EXECUTE
USER
GLOBAL
DEVICE
```

Backends may encode these differently.

The specification cares about observed access behavior.

Examples:

```text
no EXECUTE -> instruction fetch must not succeed
no USER    -> user-mode access must not succeed
no WRITE   -> write must not succeed
```

Where an architecture cannot implement a requested protection exactly, the backend must either expose an explicit capability limitation or fail the operation. Silent weakening is forbidden.

## 4. Translation visibility state

Page-table memory and processor translation caches are not assumed to become coherent automatically.

The portable kernel may request a translation synchronization transition with a defined scope.

```text
ADDRESS
ADDRESS_SPACE
GLOBAL
```

The backend must perform whatever architecture-specific ordering, invalidation, shootdown, and synchronization is required for the contract to become true.

## 5. Execution-context state

A context represents the execution state required to legally resume a kernel or user thread.

The representation is backend-private.

The semantic requirements are:

```text
suspend A
preserve all state required by the kernel ABI
prevent forbidden transient state from leaking to B
resume B in its promised execution state
```

A source and target architecture do not need identical register sets.

## 6. Privilege state

Spec-M assumes a protected-kernel model with at least:

```text
KERNEL
USER
```

Additional hardware privilege levels may exist below the Spec-M boundary.

A userspace-entry transition must establish the requested user context while preserving kernel isolation.

Required invariant:

```text
user execution cannot gain kernel privilege or access supervisor-only mappings merely because of backend implementation details
```

## 7. Interrupt/event state

The machine must permit the kernel to control whether normal maskable interrupt delivery is enabled for the current CPU and, under relevant profiles, signal other CPUs.

Portable semantics describe events, not APIC vectors, PLIC sources, GIC INTIDs, or firmware call numbers.

The backend owns routing and architecture-specific acknowledgement mechanics.

## 8. Time state

Spec-M exposes a monotonic time domain and, where the Core profile requires it, a programmable one-shot deadline.

Required properties include:

```text
time does not move backward within the defined monotonic domain
deadline requests have documented granularity/error bounds
expired deadlines eventually cause the promised event
```

Cycle counters and wall-clock calendars are separate concerns unless a profile standardizes them.

## 9. Multiprocessor state

Under the SMP profile, the machine exposes:

```text
CPU inventory
CPU identity
CPU startup
cross-CPU signaling
memory-order guarantees needed for synchronization
```

The portable kernel must not assume APIC, hart, MPIDR, or firmware-specific CPU-start vocabulary.

## 10. Memory-order state

Spec-M treats ordering as part of observable machine behavior.

The baseline vocabulary is:

```text
RELAXED
ACQUIRE
RELEASE
ACQUIRE_RELEASE
SEQUENTIALLY_CONSISTENT
```

Architecture backends must implement these semantics correctly under their native memory model.

This is especially important when translating code that was accidentally correct under x86 TSO to a weaker model such as RVWMO.

## 11. Boot state

Before portable kernel initialization begins, the backend normalizes platform/firmware information into a boot manifest.

The manifest should ultimately describe facts such as:

```text
usable physical memory
reserved physical memory
kernel image
optional initrd
CPU inventory
device/profile information
command line
early debug/console capability
```

Firmware-specific parse trees are not part of the portable machine state.

## 12. I/O state

The minimal Core substrate permits architecture/platform backends to expose MMIO safely.

Higher profiles should prefer standardized devices and buses rather than proliferating one-off device calls in the core specification.

Potential standardized profiles include:

```text
Virtio
PCIe
IOMMU/DMA
```

## 13. Lifecycle state

A conforming platform may expose:

```text
shutdown
reboot
```

The exact mechanism is backend-private.

## 14. Observable equivalence

Two backends are semantically equivalent for a transition when every observation permitted by the Spec-M contract agrees, even if their internal architecture state differs.

Example:

```text
Spec-M requirement:
    mapping is non-executable

x86-64 implementation:
    NX semantics

RV64 implementation:
    PTE X permission absent

ARM64 implementation:
    appropriate execute-never semantics
```

The backend internals differ. The kernel-visible fact is the same:

```text
instruction fetch through that mapping cannot succeed
```

## 15. Model-growth rule

Before adding a state domain or transition, require evidence that:

1. at least one real kernel needs the semantic property;
2. it cannot be expressed cleanly through existing contracts;
3. it is not merely architecture-specific historical vocabulary;
4. another architecture could implement it naturally;
5. its observable behavior can be tested.

Spec-M should become more complete through real pressure, not merely larger.
