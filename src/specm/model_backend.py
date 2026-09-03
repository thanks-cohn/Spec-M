from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModelCpu:
    cpu_id: int
    interrupts_enabled: bool = False
    active_address_space: int | None = None
    privilege: str = "kernel"
    time_value: int = 0


@dataclass
class ModelMachine:
    """A deliberately tiny deterministic state model for Spec-M contract tests.

    This is not an emulator and not a hardware backend. It exists so semantic
    transitions can be tested before being tied to x86-64 or RV64 mechanisms.
    """

    cpu_count: int = 1
    cpus: dict[int, ModelCpu] = field(init=False)
    translation_generation: dict[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.cpu_count < 1:
            raise ValueError("cpu_count must be positive")
        self.cpus = {cpu_id: ModelCpu(cpu_id) for cpu_id in range(self.cpu_count)}

    def cpu(self, cpu_id: int = 0) -> ModelCpu:
        try:
            return self.cpus[cpu_id]
        except KeyError as exc:
            raise ValueError(f"unknown cpu {cpu_id}") from exc

    def interrupt_disable(self, cpu_id: int = 0) -> None:
        self.cpu(cpu_id).interrupts_enabled = False

    def interrupt_enable(self, cpu_id: int = 0) -> None:
        self.cpu(cpu_id).interrupts_enabled = True

    def address_space_activate(self, address_space: int, cpu_id: int = 0) -> None:
        if address_space < 0:
            raise ValueError("address-space id must be non-negative")
        self.cpu(cpu_id).active_address_space = address_space
        self.translation_generation.setdefault(address_space, 0)

    def translation_sync(self, address_space: int) -> int:
        if address_space not in self.translation_generation:
            raise ValueError("address space has not been activated")
        self.translation_generation[address_space] += 1
        return self.translation_generation[address_space]

    def time_now(self, cpu_id: int = 0) -> int:
        cpu = self.cpu(cpu_id)
        value = cpu.time_value
        cpu.time_value += 1
        return value

    def userspace_enter(self, cpu_id: int = 0) -> None:
        cpu = self.cpu(cpu_id)
        if cpu.active_address_space is None:
            raise RuntimeError("userspace entry requires an active address space")
        cpu.privilege = "user"

    def snapshot(self) -> dict[str, object]:
        return {
            "cpus": {
                str(cpu_id): {
                    "interrupts_enabled": cpu.interrupts_enabled,
                    "active_address_space": cpu.active_address_space,
                    "privilege": cpu.privilege,
                    "time_value": cpu.time_value,
                }
                for cpu_id, cpu in sorted(self.cpus.items())
            },
            "translation_generation": {
                str(key): value for key, value in sorted(self.translation_generation.items())
            },
        }
