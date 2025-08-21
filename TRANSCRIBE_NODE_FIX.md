# URGENT FIX: Transcribe Voice Message Node

## 🚨 ERROR: "source.on is not a function"

**Root Cause**: HTTP Request node has conflicting content-type configuration

## 🛠️ MANUAL FIX (Required - 1 minute)

### Step 1: Open n8n Editor

1. Go to: <https://mutual-platypus-notable.ngrok-free.app>
2. Open the "Oliver" workflow
3. Find the "Transcribe Voice Message" HTTP Request node

### Step 2: Fix the Configuration

**Replace the entire HTTP Request configuration with:**

**URL:**

```
http://localhost:8000/transcribe/n8n
```

**Method:**

```
POST
```

**Headers:**

```
Content-Type: application/json
```

**Body Type:**

```
JSON (NOT multipart-form-data)
```

**JSON Body:**

```json
{
  "file_id": "={{ $json.file_id }}",
  "file_unique_id": "={{ $json.original_message.voice.file_unique_id }}",
  "duration": "={{ $json.duration }}",
  "message": "={{ $json.original_message }}"
}
```

**Timeout:**

```
30000
```

### Step 3: Save and Test

1. Save the workflow
2. Test with a voice message
3. The "source.on is not a function" error should be gone

## ✅ WHAT THIS FIXES

- ❌ **Before**: multipart-form-data + JSON headers (conflict)
- ✅ **After**: Pure JSON request (no conflict)
- ❌ **Before**: Wrong endpoint `/transcribe/file`
- ✅ **After**: Correct endpoint `/transcribe/n8n`
- ❌ **Before**: Malformed body parameters
- ✅ **After**: Clean JSON structure

## 🎯 EXPECTED RESULT

- No more "source.on is not a function" errors
- Voice messages will properly send to Whisper API
- Workflow success rate should improve dramatically

This is a **critical fix** - the current configuration is causing the HTTP Request node to fail every time it processes a voice message.
