# inventory-mcp (mock)

A minimal remote MCP server standing in for Nova Market's warehouse system. Deployed to
Cloud Run in Lab03 with `gcloud run deploy --source .` (the `Dockerfile` keeps the image lean for fast cold starts). Tools: `check_stock` (read-only),
`reserve_stock` (mutating), `whoami` (echoes request headers).
