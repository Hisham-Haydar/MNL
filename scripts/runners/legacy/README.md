# Legacy Runners

This folder contains old convenience runners that used to live at the project root.

They are kept for provenance only. Future work should prefer:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

or:

```powershell
python scripts/Job_model/run_job_ruro_pipeline.py
```

See `docs/PIPELINE_ENTRYPOINTS.md`.

