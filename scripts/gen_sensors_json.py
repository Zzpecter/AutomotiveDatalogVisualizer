import json

SIGNALS = ['Time', '  RPM', '  Sync status', '  Lost sync count', '  Injector duty', '  MAP', '  TPS', '  Primary Load', '  Secondary Load', '  Coolant Temp.', '  Intake Air Temp.', '  Battery Voltage', '  AE Delta', '  Airflow Est.', '  Fuelfow Est.', '  LC Status', '  ALS Status', '  Clutch SW Status', '  CAM A Sync Status', '  Start. Inj. Crank Trim', '  Start. Inj. ASE Trim', '  Start. Inj. ASE Decay Time', '  AE RPM Clamp Trim', '  AE VE Trim', '  AE Captured Delta', '  Lim. Table RPM', '  Lim. Ign. Cut Perc.', '  Lim. Inj. Cut Perc.', '  Extra Idle Load SW Status', '  Boost OL Duty', '  Boost CL Init Duty', '  Boost Status', '  Boost Final Duty', '  Boost P Comp.', '  Boost I Comp.', '  Boost D Comp.', '  Overrun Status', '  Ign. Dwell Base Out', '  Ign. Adv. Base Out.', '  Ign. Adv. Spark Scatter Add', '  Ign. Adv. Add. Base Out.', '  Ign. Adv. CLT Add', '  Ign. Adv. IAT Add', '  Inj. Pri. Start Angle', '  Sec. Inj. Start Angle', '  Inj. Target AFR', '  Inj. Base VE Out.', '  Inj. VE Total', '  Inj. Base PW', '  Inj. CLT Trim', '  Inj. IAT Trim', '  Inj. Idle Trim', '  Inj. Cranking Trim', '  Inj. ASE Trim', '  Inj. INT IAT Trim', '  Ign. Adv. Sec. Load Trim', '  Ign. Adv. Limiter Add', '  Ign. Adv. ALS Add', '  Inj. Add Base VE Out.', '  Inj. AE VE Added', '  Inj. Sec. Load Trim', '  Inj. Limiter Trim', '  Inj. Lambda Trim', '  Inj. Overrun Trim', '  Inj. Dead Time', '  Inj. Angle Final', '  Inj. Max Duty Cnt.', '  Trigger - Filtered IRQs', '  Master Relay Status', '  Start. Inj. ASE Decay Time Left', '  Start. Inj. Priming Pulse', '  AE CLT Trim', '  AE MAP Delta', '  AE TPS Delta', '  Lim. Hard RPM Curr.', '  Idle Ign. Adv. Spark Scatter', '  Idle OL Duty', '  Idle Target RPM', '  Idle Status', '  Idle PWM Duty', '  Idle Target RPM Err.', '  Idle P Comp.', '  Idle I Comp.', '  Idle D Comp.', '  Boost Target MAP', '  Boost Target MAP Err.', '  Lambda AFR Err. 1', '  Lambda AFR Err. 2', '  Lambda Status', '  Lambda Curr AFR 1', '  Lambda Ext. AFR', '  Lambda WB LTT Trim', '  Lambda LTT Status', '  Lambda LTT Conf. Lvl.', '  Lambda LTT Store Tmr.', '  Lambda Curr AFR 2', '  VSS Speed', '  VSS Calc. Speed', '  Sel. Map Boost', '  Ign. Adv. Final', '  Ign. Dwell Final', '  Inj. Pri. PW Final', '  Crank IRQs', '  Cam A IRQs', '  Debug 1', '  GPT 2D 1 Inp. Link', '  Int. WB Status', '  Int. WB Sensor Status', '  Int. WB HTR Drive', '  Int. WB HTR P Comp.', '  Int. WB HTR I Comp.', '  Int. WB Lambda', '  Int. WB AFR', '  CLT Out Delay', '  RTC Status', '  RTC Day', '  RTC Month', '  RTC Year', '  RTC Hour', '  RTC Minutes', '  RTC Seconds']

placeholder_signal = \
    {
        "data_type": 'float',  # int, float, bool, string, datetime, cat_string
        "category": 'TBD',  # 'AFR', 'IGN', 'TPS', 'MAP', 'TEMP', 'TIME'
        "importance": 1,  # 1 to 5 low to high
        "range": [0, 0],  # 00 no range, 0,-1 zero to infinite
        "alerts": []  # dict with type eg: warning, critical. condition eg: lt, lte, equal, gte, gt, not-equal. value
    }


signals_dict = {}
for signal in SIGNALS:
    signals_dict[signal] = placeholder_signal

with open('../datalog_visualizer/config/sensors_cfg.json', "w") as f:
    json.dump(signals_dict, f, indent=4)
