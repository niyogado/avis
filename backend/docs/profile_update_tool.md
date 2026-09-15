# Profile Update Tool

This small CLI helper lets an authorized actor request a profile update against the AVIS Core Backend.

Location: `backend/app/tools/profile_update_tool.py`

Usage examples:

```bash
# Dry-run (print JSON payload only)
python -m app.tools.profile_update_tool --token "$JWT" --full_name "Jane Doe" --print-json

# Execute update against local dev server
python -m app.tools.profile_update_tool --token "$JWT" --base-url http://localhost:8000 --full_name "Jane Doe" --headline "Product Manager"
```

Notes:
- The tool only sends fields explicitly provided on the command line and will not invent or clear fields you do not provide.
- The backend endpoint is `PUT /api/profile/` and expects a Bearer token.
- The tool requires the `requests` package, which is already in `backend/requirements.txt`.

Assistant integration:
- The assistant will use this tool (or instruct you to run it) when the user provides explicit, validated profile updates. The assistant will never modify the database directly.
