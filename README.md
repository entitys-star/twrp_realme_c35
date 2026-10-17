# Realme C35 RMX3511 — TWRP bring-up

This branch is dedicated to building a real source-built TWRP recovery for the Realme C35 (RMX3511), Android 13 firmware RMX3511T2_13.F.73.

## Status

A source-built TWRP image was produced and the first on-device test bootlooped. The failure exposed a packaging error: the generated AOSP `platform` vendor-ramdisk fragment had replaced the stock vendor runtime. The workflow now preserves the stock `platform` fragment, DTB and bootconfig, and merges only the TWRP `recovery` fragment into the original v4 image. The corrected merged image still needs a device boot test.

- Device recovery lives in `vendor_boot.img`; there is no dedicated recovery partition.
- The raw AOSP-generated `vendor_boot.img` must not be flashed directly; use only the merged final image from the corrected workflow.
- Stock `vendor_boot.img` is header v4 and 100 MiB.
- The stock `dtbo.img` has 21 FDT overlays; the observed touch coordinate space is 720 × 1600.
- The stock recovery ramdisk includes the touchscreen module set, including `sprd-focaltech.ko` and `focaltech_ft8756_spi_ts.ko`; DTBO candidates use the `oppo,touchscreen` compatible, so the active driver/panel still needs confirmation. See [touch-module audit](docs/recovery/RMX3511-touch-module-audit.md).
- The stock recovery module list has been checked against the staged ramdisk: all 157 listed modules are present, and stock `init.rc` is excluded. The device config now derives TWRP's module-load list from `modules.load.recovery`.
- AVB/rollback configuration, data decryption, and recovery boot behavior remain to be validated.

## Research

See [RMX3511 TWRP research](docs/recovery/RMX3511-TWRP-research.md).

## Branch scope

This branch intentionally excludes the kernel source and its kernel build workflows. Kernel development remains in the other branches/history of the repository. This branch is for recovery device-tree files, build configuration, and recovery-specific documentation only.
