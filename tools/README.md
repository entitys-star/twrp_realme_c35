# Recovery preparation tools

## Stage the stock recovery runtime and DTB

Run from the root of this repository with the matching stock `vendor_boot.img` and Python 3. The ramdisk extractor requires the `lz4` Python package; the staging step also requires `cpio`.

```sh
python3 -m pip install --user lz4
python3 tools/prepare_vendor_ramdisk.py /path/to/vendor_boot.img
```

The staging script now performs both required extraction steps:

- writes the complete DTB payload to `device/realme/ums9230_nico/prebuilt/dtb.img`, preserving the Android DT table if present;
- populates `device/realme/ums9230_nico/recovery/root` with the reviewed stock recovery runtime, including the module files and recovery module-load list, while refusing to copy the stock `init.rc`.

For the inspected RMX3511T2_13.F.73 image, the DTB payload is at offset 24,698,880, size 163,976 bytes, and begins with Android DT table magic `d7b7ab1e`.

## Build through GitHub Actions

The workflow `.github/workflows/build-twrp-vendor-boot.yml` uses the TWRP `twrp-12.1` manifest, stages the matching stock runtime, builds the `vendorbootimage` target, then merges only the generated `recovery` fragment into the original stock v4 image. The final artifact is `build-output/vendor_boot.img`; `vendor_boot_twrp_raw.img` is an intermediate and must not be flashed.

The workflow verifies the stock asset's SHA-256 against the inspected RMX3511T2_13.F.73 image. The corrected merge tool also checks that the original DTB, bootconfig, and every non-recovery fragment payload and metadata are preserved. These are structural checks, not proof of bootability.

- Latest workflow: [Build TWRP vendor_boot](https://github.com/entitys-star/twrp_realme_c35/actions/workflows/build-twrp-vendor-boot.yml)
- The standalone merge workflow is [Merge TWRP recovery into stock vendor_boot](https://github.com/entitys-star/twrp_realme_c35/actions/workflows/merge-twrp-vendor-boot.yml).
- On-device boot, touch, AVB/rollback behavior, USB/ADB, dynamic partition mounting, and /data decryption still require testing.

## Separate DTB extraction

If only the DTB is needed, run:

```sh
python3 tools/extract_vendor_boot_dtb.py /path/to/vendor_boot.img
```

Do not assume the device tree is build-ready or flashable after staging. Review the generated recovery root, fstab, SELinux policy handling, AVB/rollback configuration, and actual recovery boot behavior first.
