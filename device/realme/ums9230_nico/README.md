# TWRP device tree — Realme C35 (RMX3511)

**Status: source build completed; first on-device test of the unmerged image bootlooped. A corrected stock-preserving vendor_boot merge is implemented, but the corrected image has not been boot-tested.**

Target firmware: `RMX3511T2_13.F.73`, Android 13, device identity `ums9230_nico`.

## Layout

- `BoardConfig.mk`: parsed vendor_boot v4 offsets, vendor_boot output size, and TWRP settings.
- `twrp_ums9230_nico.mk`: product target.
- `recovery/root/system/etc/recovery.fstab`: stock Android v2 fstab retained for filesystem, logical-partition and encryption metadata; mount behavior is not yet device-tested.
- `recovery/root/system/etc/twrp.flags`: TWRP GUI/backup flags for boot, vendor_boot, DTBO, vbmeta, metadata, persist, misc and microSD. Verify these entries in a booted recovery before relying on backups.
- `prebuilt/dtb.img`: extract byte-for-byte from the stock `vendor_boot.img` before building. The matching 100 MiB image is recorded in the research notes (SHA-256 `17e5c60be1414e56fabfaf50887aa1e2dc910e8dc6516ad2182fce182762c4b1`). Run `python3 tools/audit_vendor_boot.py /path/to/vendor_boot.img -o /tmp/rmx3511-vendor-boot` to extract `dtb.img`, preserve the compressed vendor ramdisk, and write a hash manifest; copy the resulting `dtb.img` into `prebuilt/dtb.img`.
- `recovery/root/`: combines stock modules, module lists, ueventd rules and SELinux policy with TWRP's own init/service/USB setup. The minimal `init.recovery.ums9230_nico.rc` intentionally does not import the stock `init.recovery.common.rc`, which sets up a competing USB gadget.

## Remaining bring-up work

1. Confirm the active DTBO overlay and touch controller on the RMX3511 handset; touch support is not yet verified.
2. Check the stock FT8756 module's dependencies, firmware behavior and compatibility with the stock kernel before expecting touch to work.
3. Validate AVB/rollback behavior and the bootloader's selection of the recovery fragment.
4. Boot the corrected merged image and validate display, touch, USB/ADB, dynamic partition mounting, microSD and reboot behavior.
5. Test /data decryption and backup/restore separately. Android 13 FBE/metadata encryption is not considered supported until it is actually tested.

This tree intentionally contains no kernel source or kernel build workflow. The stock kernel stays in the original `boot.img`; the intended output is a rebuilt `vendor_boot.img`.
