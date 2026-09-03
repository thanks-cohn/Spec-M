# Spec-M Conformance

Spec-M conformance answers one question:

> Does this backend make the canonical machine semantics true on the named architecture and platform?

Compilation is not conformance.

Booting is not conformance.

A backend is conforming only to the extent that its declared Spec-M profile passes reproducible evidence.

## Evidence ladder

Spec-M uses progressively stronger evidence.

```text
C0 SPECIFIED
    backend scope and intended transition mappings are declared and validate

C1 MODEL
    deterministic semantic-model fixtures pass

C2 UNIT
    pure/backend-local and transition unit tests pass

C3 ARCH
    architecture mechanisms pass transition and negative tests

C4 PLATFORM
    tests pass under a named emulator/virtual machine/platform

C5 KERNEL
    a real kernel executes through the backend

C6 WORKLOAD
    representative real workloads exercise the contracts

C7 HARDWARE
    the declared profile passes on a named physical platform
```

Claims must name the highest level actually established.

Levels are cumulative. Evidence records are categorized as `model`, `unit`,
`architecture`, `negative`, `platform`, `kernel`, `workload`, or `hardware`.
C3 requires both architecture and negative evidence; compilation by itself is
not architecture evidence. C7 additionally requires a named physical hardware
model in the backend manifest.

## Core transition tests

The initial Core profile should gain focused tests for at least:

### Address-space activation

```text
create address space A
create address space B
map same VA to different backing pages
activate A -> observe A
activate B -> observe B
```

Negative pressure:

```text
remove permission in B
perform required translation sync
prove stale permission cannot survive
```

### Execute protection

```text
map executable page -> execution succeeds
remove execute permission
sync translation state
instruction fetch must fault/fail according to harness
```

### User/kernel isolation

```text
kernel-only mapping exists
enter user mode
user access must not succeed
kernel regains controlled execution through defined trap path
```

### Context switching

```text
A establishes unique state
switch A -> B
B establishes distinct state
switch B -> A
A resumes promised state
```

### Timer

```text
read monotonic time repeatedly -> never decreases
program future deadline -> event eventually observed
```

### Memory ordering

Conformance must include litmus/stress tests appropriate to the backend memory model.

The test intent is defined by Spec-M semantics; architecture-specific implementations may use native atomics/fences.

This is mandatory for x86-64 <-> RV64 credibility.

## SMP tests

Under the SMP profile:

```text
start secondary CPU
exchange CPU-local identities
send cross-CPU signal
stress shared state using Spec-M ordering semantics
perform translation synchronization requiring remote participation
```

A uniprocessor pass must not be used to claim SMP conformance.

## Boot-manifest tests

A platform adapter should prove that firmware/platform data is normalized correctly.

Tests should verify:

```text
usable memory does not overlap reserved regions
kernel image is represented correctly
CPU count/identity is consistent with runtime discovery
required devices/profiles are represented consistently
invalid platform data fails explicitly
```

## Differential testing

When the same test can run on multiple Spec-M backends, compare **normalized semantic traces**.

Example:

```text
backend=x86_64
address_space.activate id=4
userspace.enter ip=0x401000
fault class=execute-protection va=0x500000

backend=riscv64
address_space.activate id=4
userspace.enter ip=0x401000
fault class=execute-protection va=0x500000
```

The traces should not contain backend implementation details such as CR3 or SATP unless debugging mode explicitly requests them.

## Mutation testing

Where practical, deliberately break a backend and prove the conformance suite catches it.

Examples:

```text
omit translation fence
weaken execute protection
skip cross-CPU invalidation
use relaxed ordering where release is required
return non-monotonic synthetic time
```

A test that never fails under known broken behavior provides weak evidence.

## Platform declaration

Every conformance artifact should record:

```text
Spec-M revision
profile
backend revision
architecture
platform
firmware/emulator version where relevant
CPU count
test command
result
known deviations
```

For physical hardware, include board/model/revision information sufficient for reproduction.

## Certification language

Preferred claims:

```text
Spec-M Core C6 on RV64/QEMU-virt
Spec-M Core C7 on <named board>
Spec-M SMP C4 on x86-64/<named VM profile>
```

Avoid vague claims:

```text
"RISC-V supported"
"works on real hardware"
"fully portable"
```

unless the evidence and supported scope genuinely justify them.

## Workload pressure

Eventually, reference workloads should include increasingly difficult kernel consumers.

A useful progression is:

```text
kernel self-tests
simple userspace
ELF loader
libc/basic shell
filesystem/networking
Python
large multithreaded applications
browser-class workload
```

Spec-M does not require Linux compatibility. These workloads are pressure sources that reveal missing or incorrect machine semantics.

## Final rule

**Every Spec-M abstraction is a claim about machines. Every claim should eventually have a test capable of proving it wrong.**
