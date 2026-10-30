.. SPDX-License-Identifier: GPL-2.0+

Viettel SOVRA Rocket (CVA6) ZCU102
===================================

This is an initial, non-secure, raw-QSPI profile for a CVA6 system. It is a
source and build baseline only; it is not evidence that an FPGA image or board
boots it.

Build
-----

The requested configuration file is named ``viettel_sovra_rocket_deconfig``. It does
not follow U-Boot's usual ``*_defconfig`` filename convention, so select it
explicitly:

.. code-block:: console

   make KBUILD_DEFCONFIG=viettel_sovra_rocket_deconfig defconfig
   make CROSS_COMPILE=riscv64-linux-gnu- -j"$(nproc)"

For an out-of-tree build, pass the same ``KBUILD_DEFCONFIG`` and ``O=`` values
to the first command.

Initial boot policy
-------------------

The default environment in
``board/viettel/viettel_sovra_rocket/viettel_sovra_rocket.env`` attempts only ``boot_qspi``.
It reads a control DTB, a RISC-V Linux Image and an initrd through the approved
QSPI memory aperture, copies them to DRAM, then invokes ``booti``.

The following values are placeholders inherited from the earlier Rocket
profile and must be approved against RTL, the FPGA bitstream and the product
flash layout before board use:

* DRAM base and size;
* QSPI aperture and artifact addresses;
* UART, CLINT and PLIC addresses and clocks;
* the DT ``timebase-frequency`` value, currently 500 kHz;
* load addresses and the initrd boundary properties in the source DTB.

The profile intentionally does not add MMC, Ethernet, USB, SPI-NOR driver
support or generic distro boot targets. Add a device only after its hardware
and Driver Model contracts are proven.

Security and persistence boundary
---------------------------------

``CONFIG_FIT`` is enabled for future image packaging, but
``CONFIG_FIT_SIGNATURE`` is disabled. This board does not provide a control-DT
signature key and does not claim verified boot. The active raw-QSPI path uses
``booti`` and therefore performs no FIT signature verification.

``CONFIG_ENV_IS_NOWHERE`` is intentional. There is no saved environment,
``board_late_init()`` policy rewrite, external-NOR update command or A/B
environment layout in this initial patch. These features must be added only
with an approved flash map, erase-size evidence, readback/recovery tests and a
defined boot path for every updated artifact.
