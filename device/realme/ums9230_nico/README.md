# TWRP device tree — Realme C35 (RMX3511)

**Status: source build completed; first on-device test of the unmerged image bootlooped. A corrected stock-preserving vendor_boot merge is implemented, but the corrected image has not been boot-tested.**

Target firmware: `RMX3511T2_13.F.73`, Android 13, device identity `ums9230_nico`.

## Layout

- `BoardConfig.mk`: parsed vendor_boot v4 offsets, vendor_boot output size, and TWRP settings.
- `twrp_ums9230_nico.mk`: product target.
- `recovery/root/system/etc/recovery.fstab`: stock Android v2 fstab retained for filesystem, logical-partition and encryption metadata; mount behavior is not yet device-tested.
- `recovery/root/system/etc/twrp.flags`: TWRP GUI/backup flags for boot, vendor_boot, DTBO, vbmeta, metadata, persist, misc and microSD. Verify these entries in a booted recovery before relying on backups.
- `prebuilt/dtb.img`: extract byte-for-byte from the stock `vendor_boot.img` before building. The matching 100 MiB image is recorded in the research notes (SHA-256 `17e5c60be1414e56fabfaf50887aa1e2dc910e8dc6516ad2182fce182762c4b1`). Run `python3 tools/audit_vendor_boot.py /path/to/vendor_boot.img -o /tmp/rmx3511-vendor-boot` to extract `dtb.img`, preserve the compressed vendor ramdisk, and write a hash manifest; copy the resulting `dtb.img` into `prebuilt/dtb.img`.
- `recovery/root/`: must contain the required stock vendor ramdisk runtime and recovery init/ueventd/module/SELinux files, generated from the exact stock image.

## Build blockers

1. Stage `prebuilt/dtb.img` and stock vendor ramdisk support files from the matching firmware.
2. Generate and review the TWRP-specific `twrp.fstab`; it is not present in this scaffold yet. The stock `recovery.fstab` is only the Android recovery mount table.\n3. Confirm the correct DTBO overlay/panel identity. The overlays indicate 720×1600 coordinates and include FocalTech-specific properties, but the exact selected overlay is not yet proven.
4. Find the FT8756 firmware blob required by the touch driver; it was not found in the stock vendor ramdisk.
5. Resolve AVB: the stock vbmeta chain uses rollback-index location 18 for vendor_boot; do not use the generator's generic location 0 without proof.
6. Validate data decryption, dynamic partition mounting, USB/ADB, and bootloader recovery selection.

This tree intentionally contains no kernel source or kernel build workflow. The stock kernel stays in the original `boot.img`; the intended output is a rebuilt `vendor_boot.img`.
