#!/usr/bin/env python3
"""Merge a TWRP recovery fragment into the exact stock vendor_boot v4 image.

The stock RMX3511 vendor_boot has a platform ramdisk containing vendor init
runtime used during normal Android boot. Replacing it with the generic platform
fragment emitted by an AOSP/TWRP build can cause a bootloop. This tool preserves
all stock non-recovery fragments, the stock header/cmdline, DTB and bootconfig,
and inserts only the generated recovery fragment.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"VNDRBOOT"
HEADER_V4_MIN = 2128
RAMDISK_TYPE_RECOVERY = 2
RAMDISK_TYPE_PLATFORM = 1


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Fragment:
    entry: bytes
    payload: bytes
    name: str
    kind: int

    @property
    def is_recovery(self) -> bool:
        return self.kind == RAMDISK_TYPE_RECOVERY or self.name.lower() == "recovery"


@dataclass
class VendorBoot:
    image: bytes
    page_size: int
    header_page: bytes
    fragments: list[Fragment]
    dtb: bytes
    table_entry_size: int
    bootconfig: bytes
    header_version: int

    @classmethod
    def parse(cls, image: bytes, label: str) -> "VendorBoot":
        if len(image) < HEADER_V4_MIN or image[:8] != MAGIC:
            raise ValueError(f"{label}: not a complete vendor_boot image")
        version, page_size = struct.unpack_from("<II", image, 8)
        if version != 4:
            raise ValueError(f"{label}: expected vendor_boot header v4, got v{version}")
        if page_size < HEADER_V4_MIN or page_size & (page_size - 1):
            raise ValueError(f"{label}: invalid page size {page_size}")

        ramdisk_size = struct.unpack_from("<I", image, 24)[0]
        header_size = struct.unpack_from("<I", image, 2096)[0]
        dtb_size = struct.unpack_from("<I", image, 2100)[0]
        table_size, count, entry_size, bootconfig_size = struct.unpack_from("<IIII", image, 2112)
        if header_size < HEADER_V4_MIN or header_size > page_size:
            raise ValueError(f"{label}: invalid header size {header_size}")
        if entry_size < 108 or table_size != count * entry_size:
            raise ValueError(f"{label}: inconsistent vendor ramdisk table")

        ramdisk_start = page_size
        ramdisk_end = ramdisk_start + ramdisk_size
        dtb_start = align(ramdisk_end, page_size)
        dtb_end = dtb_start + dtb_size
        table_start = align(dtb_end, page_size)
        table_end = table_start + table_size
        bootconfig_start = align(table_end, page_size)
        bootconfig_end = bootconfig_start + bootconfig_size
        if (ramdisk_end > len(image) or dtb_end > len(image)
                or table_end > len(image) or bootconfig_end > len(image)):
            raise ValueError(f"{label}: image section extends past EOF")

        ramdisk_blob = image[ramdisk_start:ramdisk_end]
        fragments: list[Fragment] = []
        for i in range(count):
            entry = image[table_start + i * entry_size:table_start + (i + 1) * entry_size]
            size, offset, kind = struct.unpack_from("<III", entry, 0)
            name = entry[12:44].split(b"\0", 1)[0].decode("ascii", "replace")
            if size == 0 or offset + size > len(ramdisk_blob):
                raise ValueError(f"{label}: invalid ramdisk fragment {i} ({name!r})")
            fragments.append(Fragment(entry, ramdisk_blob[offset:offset + size], name, kind))

        return cls(
            image=image,
            page_size=page_size,
            header_page=image[:page_size],
            fragments=fragments,
            dtb=image[dtb_start:dtb_end],
            table_entry_size=entry_size,
            bootconfig=image[bootconfig_start:bootconfig_end],
            header_version=version,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock_vendor_boot", type=Path)
    parser.add_argument("built_vendor_boot", type=Path,
                        help="raw vendor_boot.img emitted by the TWRP build")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    stock = VendorBoot.parse(args.stock_vendor_boot.read_bytes(), "stock")
    built = VendorBoot.parse(args.built_vendor_boot.read_bytes(), "built")
    if stock.page_size != built.page_size:
        raise SystemExit("error: stock and built vendor_boot page sizes differ")
    if stock.table_entry_size != built.table_entry_size:
        raise SystemExit("error: stock and built vendor ramdisk table entry sizes differ")

    recovery = [f for f in built.fragments if f.is_recovery]
    if len(recovery) != 1:
        raise SystemExit(
            f"error: expected exactly one recovery fragment in built image; found {len(recovery)}"
        )
    twrp_recovery = recovery[0]
    stock_recovery_count = sum(f.is_recovery for f in stock.fragments)
    if stock_recovery_count > 1:
        raise SystemExit("error: stock image has multiple recovery fragments; refusing ambiguous merge")

    # Keep the stock platform/vendor runtime byte-for-byte. Replace an existing
    # recovery fragment in place, or append TWRP recovery after the stock fragments.
    merged: list[Fragment] = []
    inserted = False
    for fragment in stock.fragments:
        if fragment.is_recovery:
            merged.append(twrp_recovery)
            inserted = True
        else:
            merged.append(fragment)
    if not inserted:
        merged.append(twrp_recovery)

    ramdisk_blob = bytearray()
    table_blob = bytearray()
    for fragment in merged:
        offset = len(ramdisk_blob)
        ramdisk_blob.extend(fragment.payload)
        entry = bytearray(fragment.entry)
        struct.pack_into("<II", entry, 0, len(fragment.payload), offset)
        table_blob.extend(entry)

    header = bytearray(stock.header_page)
    struct.pack_into("<I", header, 24, len(ramdisk_blob))
    struct.pack_into("<III", header, 2112, len(table_blob), len(merged), stock.table_entry_size)
    struct.pack_into("<I", header, 2124, len(stock.bootconfig))

    output = bytearray(header)
    output.extend(ramdisk_blob)
    output.extend(b"\0" * (align(len(output), stock.page_size) - len(output)))
    output.extend(stock.dtb)
    output.extend(b"\0" * (align(len(output), stock.page_size) - len(output)))
    output.extend(table_blob)
    output.extend(b"\0" * (align(len(output), stock.page_size) - len(output)))
    output.extend(stock.bootconfig)

    partition_size = len(stock.image)
    if len(output) > partition_size:
        raise SystemExit(
            f"error: merged image is {len(output)} bytes, larger than stock partition image "
            f"({partition_size} bytes)"
        )
    output.extend(b"\0" * (partition_size - len(output)))

    # Validate the emitted layout again before writing anything.
    validated = VendorBoot.parse(bytes(output), "merged")
    if validated.dtb != stock.dtb:
        raise SystemExit("error: DTB changed during merge")
    if validated.bootconfig != stock.bootconfig:
        raise SystemExit("error: bootconfig changed during merge")
    if validated.fragments[-1].payload != twrp_recovery.payload:
        raise SystemExit("error: TWRP recovery fragment is not last in the merged table")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(f"Stock image SHA-256: {sha256(stock.image)}")
    print(f"Built image SHA-256: {sha256(built.image)}")
    print(f"Preserved stock DTB SHA-256: {sha256(stock.dtb)}")
    for fragment in validated.fragments:
        print(
            f"fragment name={fragment.name or '(unnamed)'} type={fragment.kind} "
            f"size={len(fragment.payload)} sha256={sha256(fragment.payload)}"
        )
    print(f"Merged vendor_boot size: {len(output)} bytes (partition size {partition_size})")
    print(f"Merged vendor_boot SHA-256: {sha256(bytes(output))}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
