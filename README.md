# SplitMyBillSG

A Flask bill-splitting prototype for assigning receipt items to diners, applying service charge and GST, and showing a per-person total. Manual item entry works without an OCR account; optional receipt parsing uses Mindee.

[Original video demo](https://youtu.be/E5Gc5KAqAnA) · [Application](project.py) · [Bill and payee model](classes.py)

## Run locally

Use Python 3.12:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app project run
```

Open `http://127.0.0.1:5000`. Choose the number of diners, enter their names, add or correct items, assign a payee to each item, and review the summary. The service-charge and GST switches apply 10% and 9%; the discount is divided equally between diners.

For optional OCR, set `MINDEE_API_KEY` in your local environment using your own Mindee account. No key belongs in source control. The SDK is pinned to its 4.x receipt API because this application uses `ReceiptV5`; an SDK 5.x migration is a separate compatibility change. The attempted 5.4.0 update fails at import because the 4.x `Client` interface is absent. Dependabot may propose compatible 4.x updates; major SDK updates are held until the adapter and mocked receipt tests are migrated together. Provider availability and billing are governed by your account.

## Design and privacy

- [`project.py`](project.py) implements the Flask flow and OCR adapter; [`classes.py`](classes.py) holds the bill, item and payee state.
- A bill lives in a server-side filesystem session, not an account database. Session directories are ignored by Git. `SPLITMYBILL_SESSION_DIR` chooses the local directory; `SPLITMYBILL_SECRET_KEY` can supply a persistent signing key.
- Selecting a receipt and submitting the form sends its contents to **Mindee** for parsing. Enter items manually when a receipt contains information you cannot share with that provider. Review OCR results before calculating.
- This is a local prototype. It needs additional CSRF, upload validation, financial rounding and deployment review before use as a public service. The arithmetic is not a complete accounting system.

## Verify without credentials

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip_audit -r requirements.txt
```

Tests exercise the actual Flask session flow, repeated recalculation, item removal, missing-key behavior and a mocked OCR response. They use fictional receipts and never call a paid OCR endpoint. GitHub Actions runs the same checks on pull requests and `main`.

The original project used Flowbite and Bootstrap in its interface. Third-party libraries retain their own terms; this repository currently has no declared software license.
