# Realme C35 RMX3511 — TWRP bring-up

This branch is dedicated to building a real source-built TWRP recovery for the Realme C35 (RMX3511), Android 13 firmware RMX3511T2_13.F.73.

## Status

A source-built TWRP image was produced. The first test exposed a packaging error: the generated AOSP `platform` vendor-ramdisk fragment had replaced the stock vendor runtime. The merge was corrected to preserve the stock `platform` fragment, DTB and bootconfig and add only TWRP's `recovery` fragment. On-device testing of that merged image confirms normal Android still boots, but entering recovery hangs at the Realme logo and TWRP UI never appears. The cause is not yet confirmed.

- Device recovery lives in `vendor_boot.img`; there is no dedicated recovery partition.
- The raw AOSP-generated `vendor_boot.img` must not be flashed directly; use only the merged final image from the corrected workflow.
- Stock `vendor_boot.img` is header v4 and 100 MiB.
- The stock `dtbo.img` has 21 FDT overlays. The supplied boot command line identifies `androidboot.dtbo_idx=12`, `lcd_name=lcd_NT36672C_csot_mipi_hd` and `lcd_size=2408x1080`; the build config now sets TWRP's logical screen size to 1080 × 2408.
- Overlay 12 belongs to the Novatek/CSOT candidate group (overlays 6–13); `sprd-nt36xxx.ko` is the leading touchscreen-driver candidate. The exact active overlay/driver and backlight path still require on-device confirmation. See [touch-module audit](docs/recovery/RMX3511-touch-module-audit.md).
- The stock recovery module list has been checked against the staged ramdisk: all 157 listed modules are present, and stock `init.rc` is excluded. The device config now derives TWRP's module-load list from `modules.load.recovery`.
- Stock `init.recovery.common.rc` is also excluded: it starts a competing Unisoc configfs/USB setup and stock vendor services. A minimal device-specific init file leaves service/USB setup to TWRP. The board init sets `sys.usb.configfs=1` and `sys.usb.controller=musb-hdrc.1.auto`, based on values observed with `getprop` in stock Android. These properties have **not** been independently verified in stock recovery, and USB gadget operation in TWRP remains unverified.
- The device config points TWRP brightness control at `/sys/class/backlight/sprd_backlight/brightness` with maximum 4095. The default value 2048 is a provisional midpoint, not a measured stock default.
- TWRP-specific backup flags now expose `boot`, `vendor_boot`, `dtbo`, vbmeta partitions, `metadata`, `persist`, `misc` and microSD; their behavior has not yet been verified in a running recovery.
- AVB/rollback configuration, data decryption, and recovery boot behavior remain to be validated.

## TODO / validation checklist

Checked items are completed by repository/static checks; unchecked items still need evidence. After each on-device check, report the result and this list will be updated. A successful build alone does **not** mean TWRP boots.

- [x] Preserve the stock `platform` vendor-ramdisk fragment, DTB and bootconfig when merging.
- [x] Validate merged image structure and enforce preservation checks in the merge script.
- [x] Confirm all 157 modules listed in stock `modules.load.recovery` exist in the staged ramdisk.
- [x] Exclude stock recovery init scripts that conflict with TWRP's USB/service setup.
- [x] Add TWRP partition flags and Android 13 FBE build options (runtime behavior remains unverified).
- [x] Escape both shell references as `$module` in `TW_LOAD_VENDOR_MODULES` so Make passes `$module` through to the shell, and set screen dimensions to 1080 × 2408 from the supplied boot command line.
- [x] Set `PRODUCT_SHIPPING_API_LEVEL := 30` to match the device's first API level.
- [x] Restrict builds to manual `workflow_dispatch`, remove the obsolete separate merge workflow, and switch disk-space action to `@v10`.
- [x] Add a GitHub Actions cache for TWRP repo metadata; remove the redundant `BUILDING_VENDOR_BOOT_IMAGE` export.
- [ ] Build the latest revision successfully and inspect the final merged artifact.
- [ ] Boot the merged image into TWRP on the RMX3511 without breaking normal Android boot.
- [ ] Verify touchscreen input, orientation and full-screen coordinates.
- [ ] Verify MTP / ADB and external microSD access.
- [ ] Verify partition list, backup/restore and slot handling.
- [ ] Verify /data decryption on the installed Android 13 firmware.
- [ ] Resolve and verify AVB / rollback-index behavior.
- [ ] Confirm the exact DTBO touchscreen overlay and active touchscreen driver.
- [x] Set `TW_BRIGHTNESS_PATH` and `TW_MAX_BRIGHTNESS` from the observed `/sys/class/backlight/sprd_backlight/` node (runtime brightness control still needs testing).
- [ ] Confirm which slot has kernel vermagic `5.4.254-android12-9-…-ab1584`; do not test the image against the `ab1209` kernel.
- [ ] Back up both `vendor_boot_a` and `vendor_boot_b` before any flash test.
- [ ] Resolve whether the Unisoc bootloader starts both PLATFORM and RECOVERY fragments, and validate AVB/vbmeta behavior.
- [ ] Complete a recovery reboot, normal Android reboot and power-off/restart test.

## Research and audits
- [`docs/recovery/RMX3511-TWRP-research.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-TWRP-research.md)
- [`docs/recovery/RMX3511-extraction-results.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-extraction-results.md)
- [`docs/recovery/RMX3511-touch-module-audit.md`](https://raw.githubusercontent.com/entitys-star/twrp_realme_c35/main/docs/recovery/RMX3511-touch-module-audit.md)

## Research

See [RMX3511 TWRP research](docs/recovery/RMX3511-TWRP-research.md).

## Branch scope

This branch intentionally excludes the kernel source and its kernel build workflows. Kernel development remains in the other branches/history of the repository. This branch is for recovery device-tree files, build configuration, and recovery-specific documentation only.
