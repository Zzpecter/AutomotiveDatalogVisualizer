import os

COL_RPM = ' RPM'
COL_MAP = ' MAP'
COL_AFR = ' Int. WB AFR'
COL_COOLANT = ' Coolant Temp.'
COL_TPS = ' TPS'

X_TICKS = [500, 800, 1100, 1400, 2000, 2600, 3100, 3700, 4300, 4900, 5400, 6000, 6500, 7000, 7200, 7500]
Y_TICKS = [20, 25, 30, 45, 55, 65, 75, 85, 95, 100, 120, 140, 160, 190, 225, 250]

TARGET_AFR_JSON_PATH = os.path.join(os.path.dirname(__file__), 'target_afr.json')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'sensors_cfg.json')

conditions_fwd = {
    'EQUAL': 'eq',
    'NOT EQUAL': 'neq',
    'LOWER THAN': 'lt',
    'LOWER-EQUAL THAN': 'lte',
    'GREATER-EQUAL THAN': 'gte',
    'GREATER THAN': 'gt',
}
conditions_bwd = {v: k for k, v in conditions_fwd.items()}
CONDITIONS_DICT = {**conditions_fwd, **conditions_bwd}
