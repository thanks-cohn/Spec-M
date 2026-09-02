# Spec-M Design Principles

Spec-M exists to define a small, durable machine contract for kernels.

These principles are stronger than convenience. They are the criteria by which new primitives and backends should be judged.

## 1. Standardize semantics, not historical mechanisms

A common-kernel interface should describe the property the kernel needs, not the instruction or device that one machine uses.

Prefer:

```text
activate address space
synchronize translations
enter userspace
send CPU event
program deadline
publish memory with release ordering
```

Avoid:

```text
write CR3
invalidate page with INVLPG
send APIC vector
execute SRET
call SBI extension X
```

Architecture-specific names belong in backends.

## 2. Observable equivalence is enough

A real backend does not need to reproduce the internal state of the abstract machine bit-for-bit.

It must reproduce the behavior the kernel is permitted to observe.

For any Spec-M transition:

```text
precondition
    + transition
        -> postcondition
```

a conforming backend must make the postcondition true under the same contractual assumptions.

This is the basis for implementing the same Spec-M contract with radically different CPUs.

## 3. The common machine must be smaller than the machines below it

Spec-M is not useful if it becomes the union of x86, RISC-V, ARM, every firmware standard, and every device ever shipped.

A primitive enters Spec-M because multiple real kernels require the semantic capability, not because a backend exposes it.

The common machine should remain aggressively small.

## 4. Capabilities are explicit

Optional hardware features must appear as capabilities or profiles.

A kernel may require them.

A backend may advertise them.

The system must not silently fake a stronger machine than exists.

## 5. Protection semantics are normative

Correctness is not merely reaching the next boot message.

The specification must make security-relevant state transitions explicit:

```text
user/supervisor privilege
read/write/execute permissions
address-space isolation
translation invalidation
interrupt masking
DMA visibility
memory ordering
```

A backend that boots but violates these properties is non-conforming.

## 6. Ordering is part of behavior

Memory ordering cannot be treated as backend trivia.

Spec-M must state ordering guarantees at the semantic boundary so a kernel that was accidentally correct on x86 TSO does not become silently incorrect on RVWMO or another weaker model.

The common contract should express intent such as:

```text
relaxed
acquire
release
acquire-release
sequentially consistent
```

or a stronger domain-specific invariant where required.

## 7. Firmware is an input format, not the kernel model

UEFI, ACPI, Device Tree, SBI, Multiboot, and platform firmware are useful standards.

They should be translated by a backend into a normalized Spec-M boot representation.

The portable kernel should consume facts, not firmware history.

## 8. Reuse successful standards below the boundary

Spec-M should compose rather than replace standards that already work well.

Examples include:

```text
ELF
Virtio
PCIe
UEFI where appropriate
SBI where appropriate
Device Tree / ACPI as backend discovery sources
```

The project's novelty is the canonical kernel-visible machine, not ownership of every layer.

## 9. A backend is a proof obligation

Implementing function names is insufficient.

Every backend must provide reproducible evidence that its state transitions satisfy Spec-M.

Tests should include positive, negative, stress, and integration cases.

## 10. Real hardware claims are platform-specific

`riscv64` is not a real-hardware certification by itself.

A claim should name enough of the platform to be reproducible, for example:

```text
Spec-M Core / RV64 / QEMU virt
Spec-M Core / RV64 / board-X revision-Y
Spec-M Core / x86-64 / UEFI-PC profile
```

Architecture conformance and platform conformance are related but distinct.

## 11. X-REF targets Spec-M

X-REF should increasingly treat Spec-M as its destination architecture boundary.

Instead of translating x86 implementation directly to RISC-V implementation:

```text
source assumption
    -> semantic classification
        -> Spec-M contract
            -> preserve source
                -> choose target backend
```

This reduces lateral translation and makes one migration reusable across multiple target machines.

## 12. Z-REF is pressure, not authority

A working reference implementation is invaluable, but no one implementation defines Spec-M by itself.

Z-REF can demonstrate that a proposed machine primitive is useful and sufficient.

Other kernels and architectures can reveal that the abstraction is too narrow, too broad, or accidentally source-specific.

Spec-M should converge through multiple implementations and workloads.

## 13. The next architecture should be imaginable

Before accepting a common primitive, ask:

> Could a third architecture implement this naturally without pretending to be either of the first two?

If not, reconsider the abstraction.

## 14. The next kernel should be cheaper

Every validated backend, migrated kernel, failure signature, and conformance test should reduce rediscovery for the next project.

Spec-M succeeds only if portability knowledge accumulates.

## 15. Simplicity is a technical requirement

The machine contract should remain understandable enough that a kernel author, reviewer, or agent can reason about the complete boundary.

A tiny well-proved interface is preferable to a comprehensive interface whose semantics cannot be held in one mental model.
