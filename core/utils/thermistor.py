# Temperature measurements with thermistors
#
# Copyright (C) 2016-2019  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math, logging


KELVIN_TO_CELSIUS = -273.15


class NTCReg:
    t1 = 0
    t2 = 0
    t3 = 0
    r1 = 0
    r2 = 0
    r3 = 0
    beta = 0

    def __init__(self, type, use_beta):
        self.type = type
        self.use_beta = use_beta
        self._init_reg()

    def _generate_coefficients(self, beta, t1, r1, t2, r2, t3, r3):
        NTCReg.t1 = t1
        NTCReg.t2 = t2
        NTCReg.t3 = t3
        NTCReg.r1 = r1
        NTCReg.r2 = r2
        NTCReg.r3 = r3
        if self.use_beta:
            NTCReg.beta = beta

    def _init_reg(self):
        if self.type == "NTC_100K_4_R025H4G":
            # https://www.mouser.com/datasheet/2/362/P18_NT_Thermistor-1535133.pdf
            self._generate_coefficients(
                4267, 25.0, 100000.0, 40.0, 33450.0, 80.0, 10800.0
            )


# Analog voltage to temperature converter for thermistors
class Thermistor:
    def __init__(self, pullup, inline_resistor):
        self.pullup = pullup
        self.inline_resistor = inline_resistor
        self.c1 = self.c2 = self.c3 = 0.0

    def setup_coefficients(self, t1, r1, t2, r2, t3, r3, name=""):
        from core.utils.opt_log import GlobalLogger

        # Calculate Steinhart-Hart coefficents from temp measurements.
        # Arrange samples as 3 linear equations and solve for c1, c2, and c3.
        inv_t1 = 1.0 / (t1 - KELVIN_TO_CELSIUS)
        inv_t2 = 1.0 / (t2 - KELVIN_TO_CELSIUS)
        inv_t3 = 1.0 / (t3 - KELVIN_TO_CELSIUS)
        ln_r1 = math.log(r1)
        ln_r2 = math.log(r2)
        ln_r3 = math.log(r3)
        ln3_r1, ln3_r2, ln3_r3 = ln_r1**3, ln_r2**3, ln_r3**3

        inv_t12, inv_t13 = inv_t1 - inv_t2, inv_t1 - inv_t3
        ln_r12, ln_r13 = ln_r1 - ln_r2, ln_r1 - ln_r3
        ln3_r12, ln3_r13 = ln3_r1 - ln3_r2, ln3_r1 - ln3_r3

        self.c3 = (inv_t12 - inv_t13 * ln_r12 / ln_r13) / (
            ln3_r12 - ln3_r13 * ln_r12 / ln_r13
        )
        if self.c3 <= 0.0:
            beta = ln_r13 / inv_t13
            GlobalLogger.debug_print(f"calc beta is  {beta}")
            self.setup_coefficients_beta(t1, r1, beta)
            return
        self.c2 = (inv_t12 - self.c3 * ln3_r12) / ln_r12
        self.c1 = inv_t1 - self.c2 * ln_r1 - self.c3 * ln3_r1

    def setup_coefficients_beta(self, t1, r1, beta):
        # Calculate equivalent Steinhart-Hart coefficents from beta
        inv_t1 = 1.0 / (t1 - KELVIN_TO_CELSIUS)
        ln_r1 = math.log(r1)
        self.c3 = 0.0
        self.c2 = 1.0 / beta
        self.c1 = inv_t1 - self.c2 * ln_r1

    def calc_temp(self, adc):
        # Calculate temperature from adc
        adc = max(0.00001, min(0.99999, adc))
        r = self.pullup * adc / (1.0 - adc)
        ln_r = math.log(r - self.inline_resistor)
        inv_t = self.c1 + self.c2 * ln_r + self.c3 * ln_r**3
        return round(1.0 / inv_t + KELVIN_TO_CELSIUS, 2)

    def calc_adc(self, temp):
        # Calculate adc reading from a temperature
        if temp <= KELVIN_TO_CELSIUS:
            return 1.0
        inv_t = 1.0 / (temp - KELVIN_TO_CELSIUS)
        if self.c3:
            # Solve for ln_r using Cardano's formula
            y = (self.c1 - inv_t) / (2.0 * self.c3)
            x = math.sqrt((self.c2 / (3.0 * self.c3)) ** 3 + y**2)
            ln_r = math.pow(x - y, 1.0 / 3.0) - math.pow(x + y, 1.0 / 3.0)
        else:
            ln_r = (inv_t - self.c1) / self.c2
        r = math.exp(ln_r) + self.inline_resistor
        return r / (self.pullup + r)


# Custom defined thermistors from the config file
class CustomThermistor:

    def __init__(self):
        from core.utils.common import GlobalComm

        ntcReg = NTCReg(GlobalComm.setting_json["temp_type"], False)
        t1 = ntcReg.t1
        r1 = ntcReg.r1
        beta = ntcReg.beta
        if beta is not None and beta != 0:
            self.params = {"t1": t1, "r1": r1, "beta": beta}
            return
        t2 = ntcReg.t2
        r2 = ntcReg.r2
        t3 = ntcReg.t3
        r3 = ntcReg.r3
        (t1, r1), (t2, r2), (t3, r3) = sorted([(t1, r1), (t2, r2), (t3, r3)])
        self.params = {"t1": t1, "r1": r1, "t2": t2, "r2": r2, "t3": t3, "r3": r3}

        self._init_printer_thermistor(self.params)

    def _init_printer_thermistor(self, params):
        from core.utils.common import GlobalComm
        from core.utils.opt_log import GlobalLogger

        pullup = float(GlobalComm.setting_json["temp_pullup_resistor"])
        inline_resistor = 0

        self.thermistor = Thermistor(pullup, inline_resistor)
        if "beta" in params:
            self.thermistor.setup_coefficients_beta(
                params["t1"], params["r1"], params["beta"]
            )
            GlobalLogger.debug_print("use beta to set temp")
        else:
            self.thermistor.setup_coefficients(
                params["t1"],
                params["r1"],
                params["t2"],
                params["r2"],
                params["t3"],
                params["r3"],
            )
            GlobalLogger.debug_print("calculate beta value to set temp")

    def get_temp(self, adc_val):
        adc_max_range = 4095.0
        return self.thermistor.calc_temp(adc_val / adc_max_range)
