# Completion review

**Verdict: incomplete.** The requested outcome is saving filters, closing the app, and loading those same filters on the next launch. The application reports a successful save, but the next launch returns `None`.

## Blocking finding

`presets.py:2-6` stores presets only in the process-local `PRESETS` dictionary. Each CLI invocation initializes an empty dictionary. There is no durable write or read, so closing the application discards the saved filters.

I exercised the documented application entry point in separate processes in the same fixture directory:

```text
$ python3 presets.py save weekly last_7_days
Saved weekly
exit_code=0
$ python3 presets.py load weekly
None
exit_code=0
```

The expected consumer result on the second launch is `last_7_days`. This observed failure directly contradicts the original request.

## Supplied checks and boundary

`python3 test_presets.py` passes (one test). `test_presets.py:5-7` calls `save` and `load` inside the same imported module and process. It demonstrates an in-memory round trip but bypasses the documented CLI and never crosses the close/relaunch boundary. The central promised action can therefore fail while every supplied assertion passes.

The review used the original request as its acceptance criterion and applied `instructions/guidance.md` and `instructions/proof.md`. Input was the CLI filter string, activation was the documented save command, and the consumer observation was a fresh-process load command. No fake or prefilled state was used. Actual investigation commands and stdout/stderr are retained in `tool-events.log`.

## Limits and ownership

This establishes failure in the supplied local CLI implementation. No separate GUI or deployed target was supplied or assessed. Application code and supplied checks were left unchanged. The implementation owner must provide persistence across launches; subsequent acceptance evidence must repeat save and load across separate application processes. No extra product decision is needed to establish that requirement.
