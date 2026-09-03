# RV64 architecture boundary

This layer may use RV64 architectural mechanisms to realize canonical transitions.
It must not parse device trees, select QEMU devices, or assume SBI services.  The
first pressure is `time.h`: a compilable read of architectural time ticks.  Ticks
are deliberately not advertised as `specm_time_now` until the platform supplies
and validates a timebase and monotonic conversion.
