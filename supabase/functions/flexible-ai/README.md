# Flexible AI Edge Function

This Supabase Edge Function provides a secure proxy for the NVIDIA DeepSeek API.

## Setup

### 1. Deploy the function

```bash
supabase functions deploy flexible-ai
```

### 2. Set the API key as a secret

**IMPORTANT**: Never expose the API key in client-side code!

```bash
supabase secrets set NVIDIA_API_KEY=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
```

Or via the Supabase Dashboard:
1. Go to **Settings** > **Edge Functions**
2. Add a new secret: `NVIDIA_API_KEY`
3. Paste your API key

### 3. Test the function

```bash
curl -X POST 'https://YOUR-PROJECT.supabase.co/functions/v1/flexible-ai' \
  -H 'Authorization: Bearer YOUR_ANON_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "stream": false}'
```

## Features

- **Secure API Key**: Key stored in Supabase secrets, never exposed
- **Streaming**: Supports real-time streaming responses
- **Tool Calling**: AI can create pipelines, execute them, etc.
- **CORS**: Configured for cross-origin requests

## Tools Available

| Tool | Description |
|------|-------------|
| `create_pipeline` | Create a new data pipeline |
| `execute_pipeline` | Run an existing pipeline |
| `list_pipelines` | Get all available pipelines |
| `get_pipeline_status` | Check execution status |
| `get_ai_insights` | Retrieve AI insights |
| `navigate_to` | Navigate user to a page |
