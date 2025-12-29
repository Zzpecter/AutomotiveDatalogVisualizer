def safe_divide(numerator, denominator, fallback=0.0):
    return numerator / denominator if denominator != 0 else fallback


def unit_converter(value, unit_from, unit_to):
    conversions = {
        ('C', 'F'): lambda v: (v * 9 / 5) + 32,
        ('F', 'C'): lambda v: (v - 32) * 5 / 9,
        ('Bar', 'PSI'): lambda v: v * 14.5038,
        ('kPa', 'PSI'): lambda v: v * 0.145038,
        ('Lambda', 'AFR'): lambda v: v * 14.7,
    }
    return conversions.get((unit_from, unit_to), lambda v: v)(value)
