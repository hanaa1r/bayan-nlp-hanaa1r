# BENCHMARKS draft — PROJECT_ARTIFACT

- Result label: `MEASURED`
- Decision scope: `PROJECT_BUDGET_DECISION`
- Workload SHA-256: `9b07010d0e607282b66a0a1b1096175fd6015a237577db26bf03366393e077d8`
- Device/provider: `cpu` / `CPUExecutionProvider`
- Warm-up/repetitions: 5/30
- Memory method: process RSS start and observed peak; approximate
- PyTorch p95: 253.711 ms
- ONNX FP32 p95: 336.370 ms
- ONNX FP32 quality tax: 0.000000
- INT8 available: True
- Selected for service: `pytorch-fp32`

- Adoption decision: `KEEP_PYTORCH_FP32`

> Replace this smoke draft with the complete BENCHMARKS template and full project workload before Gate D.
