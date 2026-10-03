# Demo data

`demo-run.json` and `public/demo-glucose.csv` are wholly synthetic. They are not Greg's actual run or any patient's CGM export. `scripts/build_demo.py` regenerates both with seed 20261003.

94 minutes of synthetic pace/HR/elevation, a CGM series and a deliberate missing interval between minute 25 and 50. Three selected windows show missing glucose, a steady segment and low glucose + uphill. Illustrative UI fixtures, not clinical validation or automatic engine detection.

Coverage counts only adjacent readings at most 10 minutes apart: 69/94 minutes rounds to 73%. Minimum 65 mg/dL; two points below 70, none below 54. No time below threshold inferred. The final interval is four minutes, ending at minute 94. CSV timestamps are local Europe/Warsaw; synthetic start 08:30 on October 3.

Original `example.json` remains a disclosed pre-event neutral fixture, unused by this UI.
