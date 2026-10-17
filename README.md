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
- Stock `init.recovery.common.rc` is also excluded: it starts a competing Unisoc configfs/USB setup and stock vendor services. A minimal device-specific init file leaves service/USB setup to TWRP.
- TWRP-specific backup flags now expose `boot`, `vendor_boot`, `dtbo`, vbmeta partitions, `metadata`, `persist`, `misc` and microSD; their behavior has not yet been verified in a running recovery.
- AVB/rollback configuration, data decryption, and recovery boot behavior remain to be validated.


## TODO / validation checklist

Checked items are completed by repository/static checks; unchecked items still need evidence. After each on-device check, report the result and this list will be updated. A successful build alone does **not** mean TWRP boots.

- [x] Preserve the stock `platform` vendor-ramdisk fragment, DTB and bootconfig when merging.
- [x] Validate merged image structure and enforce preservation checks in the merge script.
- [x] Confirm all 157 modules listed in stock `modules.load.recovery` exist in the staged ramdisk.
- [x] Exclude stock recovery init scripts that conflict with TWRP's USB/service setup.
- [x] Add TWRP partition flags and Android 13 FBE build options (runtime behavior remains unverified).
- [ ] Build the latest revision successfully and inspect the final merged artifact.
- [ ] Boot the merged image into TWRP on the RMX3511 without breaking normal Android boot.
- [ ] Verify touchscreen input, orientation and full-screen coordinates.
- [ ] Verify MTP / ADB and external microSD access.
- [ ] Verify partition list, backup/restore and slot handling.
- [ ] Verify /data decryption on the installed Android 13 firmware.
- [ ] Resolve and verify AVB / rollback-index behavior.
- [ ] Confirm the exact DTBO touchscreen overlay and active touchscreen driver.
- [ ] Complete a recovery reboot, normal Android reboot and power-off/restart test.

## Source files (raw links for external review)

Each link below opens the **raw file contents**; the repository path is written beside it so the reviewer can identify the file.

### Build workflows
- [`.github/workflows/build-twrp-vendor-boot.yml`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/.github/workflows/build-twrp-vendor-boot.yml)
- [`.github/workflows/merge-twrp-vendor-boot.yml`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/.github/workflows/merge-twrp-vendor-boot.yml)

### Device tree
- [`device/realme/ums9230_nico/AndroidProducts.mk`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/AndroidProducts.mk)
- [`device/realme/ums9230_nico/BoardConfig.mk`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/BoardConfig.mk)
- [`device/realme/ums9230_nico/README.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/README.md)
- [`device/realme/ums9230_nico/device.mk`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/device.mk)
- [`device/realme/ums9230_nico/twrp_ums9230_nico.mk`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/twrp_ums9230_nico.mk)
- [`device/realme/ums9230_nico/recovery/root/init.recovery.ums9230_nico.rc`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/recovery/root/init.recovery.ums9230_nico.rc)
- [`device/realme/ums9230_nico/recovery/root/system/etc/recovery.fstab`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/recovery/root/system/etc/recovery.fstab)
- [`device/realme/ums9230_nico/recovery/root/system/etc/twrp.flags`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/device/realme/ums9230_nico/recovery/root/system/etc/twrp.flags)

### Build and image tools
- [`tools/README.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/README.md)
- [`tools/audit_vendor_boot.py`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/audit_vendor_boot.py)
- [`tools/extract_vendor_boot_dtb.py`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/extract_vendor_boot_dtb.py)
- [`tools/extract_vendor_boot_ramdisk.py`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/extract_vendor_boot_ramdisk.py)
- [`tools/merge_vendor_boot_recovery.py`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/merge_vendor_boot_recovery.py)
- [`tools/prepare_vendor_ramdisk.py`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/tools/prepare_vendor_ramdisk.py)

### Research and audits
- [`docs/recovery/RMX3511-TWRP-research.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-TWRP-research.md)
- [`docs/recovery/RMX3511-extraction-results.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-extraction-results.md)
- [`docs/recovery/RMX3511-touch-module-audit.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-touch-module-audit.md)

## Research

See [RMX3511 TWRP research](docs/recovery/RMX3511-TWRP-research.md).

## Branch scope

This branch intentionally excludes the kernel source and its kernel build workflows. Kernel development remains in the other branches/history of the repository. This branch is for recovery device-tree files, build configuration, and recovery-specific documentation only.
