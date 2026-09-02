#ifndef SPECM_MACHINE_H
#define SPECM_MACHINE_H

/*
 * Spec-M canonical machine contract.
 *
 * This header is intentionally small and semantic. It describes the machine
 * state and transitions a portable kernel may depend upon. Architecture and
 * platform backends are responsible for mapping real mechanisms onto these
 * contracts and proving conformance.
 *
 * Draft: interfaces may change as real kernels and backends pressure them.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint64_t specm_cpu_id_t;
typedef uint64_t specm_phys_addr_t;
typedef uint64_t specm_virt_addr_t;
typedef uint64_t specm_asid_t;
typedef uint64_t specm_time_t;

enum specm_status {
    SPECM_OK = 0,
    SPECM_UNSUPPORTED,
    SPECM_INVALID,
    SPECM_DENIED,
    SPECM_BUSY,
    SPECM_FAILED
};

enum specm_capability {
    SPECM_CAP_USER_MODE               = 1ull << 0,
    SPECM_CAP_SMP                     = 1ull << 1,
    SPECM_CAP_ADDRESS_SPACE_TAGS      = 1ull << 2,
    SPECM_CAP_PRECISE_DEADLINE_TIMER  = 1ull << 3,
    SPECM_CAP_DMA                     = 1ull << 4,
    SPECM_CAP_PCIE                    = 1ull << 5,
    SPECM_CAP_VIRTIO                  = 1ull << 6,
    SPECM_CAP_HW_VIRTUALIZATION       = 1ull << 7
};

enum specm_memory_order {
    SPECM_ORDER_RELAXED = 0,
    SPECM_ORDER_ACQUIRE,
    SPECM_ORDER_RELEASE,
    SPECM_ORDER_ACQ_REL,
    SPECM_ORDER_SEQ_CST
};

enum specm_translation_scope {
    SPECM_TRANSLATION_ADDRESS = 0,
    SPECM_TRANSLATION_ADDRESS_SPACE,
    SPECM_TRANSLATION_GLOBAL
};

enum specm_map_permissions {
    SPECM_MAP_READ    = 1u << 0,
    SPECM_MAP_WRITE   = 1u << 1,
    SPECM_MAP_EXECUTE = 1u << 2,
    SPECM_MAP_USER    = 1u << 3,
    SPECM_MAP_GLOBAL  = 1u << 4,
    SPECM_MAP_DEVICE  = 1u << 5
};

enum specm_cpu_signal_kind {
    SPECM_CPU_SIGNAL_RESCHEDULE = 0,
    SPECM_CPU_SIGNAL_TLB_SYNC,
    SPECM_CPU_SIGNAL_GENERIC
};

struct specm_machine_info {
    const char *architecture;
    const char *platform;
    uint64_t capabilities;
    uint32_t cpu_count;
    uint32_t base_page_shift;
};

struct specm_address_space {
    specm_phys_addr_t root;
    specm_asid_t id;
    uint64_t backend_private;
};

struct specm_kernel_context {
    uint64_t opaque[40];
};

struct specm_user_context {
    specm_virt_addr_t instruction_pointer;
    specm_virt_addr_t stack_pointer;
    specm_virt_addr_t thread_pointer;
    uint64_t opaque[32];
};

struct specm_cpu_signal {
    enum specm_cpu_signal_kind kind;
    uint64_t value;
};

struct specm_memory_region {
    specm_phys_addr_t base;
    uint64_t length;
    uint32_t flags;
};

struct specm_boot_manifest {
    const struct specm_memory_region *memory_regions;
    size_t memory_region_count;

    specm_phys_addr_t kernel_base;
    uint64_t kernel_size;

    specm_phys_addr_t initrd_base;
    uint64_t initrd_size;

    const char *command_line;
    uint64_t backend_private;
};

/* Discovery */
const struct specm_machine_info *specm_machine_info(void);
bool specm_machine_has(enum specm_capability capability);
const struct specm_boot_manifest *specm_boot_manifest(void);

/* CPU state */
specm_cpu_id_t specm_cpu_current(void);
void specm_cpu_relax(void);
void specm_cpu_halt(void);
enum specm_status specm_cpu_start(specm_cpu_id_t cpu, specm_phys_addr_t entry, uint64_t opaque);
enum specm_status specm_cpu_signal(specm_cpu_id_t cpu, const struct specm_cpu_signal *signal);

/* Interrupt state */
void specm_interrupt_disable(void);
void specm_interrupt_enable(void);
bool specm_interrupt_enabled(void);

/* Address-space state */
enum specm_status specm_address_space_activate(const struct specm_address_space *space);
enum specm_status specm_translation_sync(
    const struct specm_address_space *space,
    specm_virt_addr_t address,
    enum specm_translation_scope scope);

/* Execution state */
void specm_context_switch(
    struct specm_kernel_context *outgoing,
    const struct specm_kernel_context *incoming);

void specm_userspace_enter(const struct specm_user_context *context);

/* Time */
specm_time_t specm_time_now(void);
enum specm_status specm_timer_set_deadline(specm_time_t deadline);

/* Ordering */
void specm_memory_fence(enum specm_memory_order order);

/* Minimal physical I/O substrate */
enum specm_status specm_mmio_read32(specm_phys_addr_t address, uint32_t *value);
enum specm_status specm_mmio_write32(specm_phys_addr_t address, uint32_t value);

/* Lifecycle */
void specm_shutdown(void);
void specm_reboot(void);

#ifdef __cplusplus
}
#endif

#endif /* SPECM_MACHINE_H */
