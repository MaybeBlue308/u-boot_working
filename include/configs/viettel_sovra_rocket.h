/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Board-specific options belong in Kconfig, the control DT and the
 * board environment. This header exists because SYS_CONFIG_NAME requires it.
 */

#ifndef __CONFIG_VIETTEL_SOVRA_ROCKET_H
#define __CONFIG_VIETTEL_SOVRA_ROCKET_H

#define BOOT_TARGET_DEVICES(func) func(SOVRA_QSPI, qspi, na)
#define BOOTENV_DEV_SOVRA_QSPI(devtypeu, devtypel, instance) \
	"bootcmd_qspi=run boot_qspi\0"
#define BOOTENV_DEV_NAME_SOVRA_QSPI(devtypeu, devtypel, instance) "qspi "

#include <config_distro_bootcmd.h>

#define CFG_EXTRA_ENV_SETTINGS BOOTENV

#endif
