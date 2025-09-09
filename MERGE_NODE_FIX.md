# n8n Merge Node Quick Fix Guide

## 🚨 URGENT: Merge Node Not Outputting File Data

### Step 1: Check "Get a file" Node Output

1. Open n8n editor: <https://mutual-platypus-notable.ngrok-free.app>
2. Click on "Get a file" node
3. Click "Execute Node" (test it independently)
4. Verify output contains:

   ```json
   {
     "file_id": "...",
     "file_path": "...", 
     "file_size": "...",
     "mime_type": "..."
   }
   ```

### Step 2: Check Merge Node Configuration

1. Click on the Merge node
2. Set these parameters:
   - **Mode**: "Append" (or try "Keep Key Matches")
   - **Output Data**: "All Inputs"
   - **Join**: Leave default

### Step 3: Verify Connections

1. Ensure connection from "Get a file" → Merge node (Input 1)
2. Ensure connection from previous trigger → Merge node (Input 2)
3. Ensure connection from Merge node → "Transcribe Voice Message"

### Step 4: Test Merge Node

1. Click on Merge node
2. Click "Execute Node"
3. Check output contains BOTH:
   - File data from "Get a file"
   - Message data from trigger

### Alternative: Bypass Merge Node

If merge continues to fail, you can bypass it:

1. Connect "Get a file" directly to "Transcribe Voice Message"
2. Update "Transcribe Voice Message" node to get message data from:
   - `{{ $('Telegram Trigger').first().json }}`

### Expected Data Structure

The merge node should output:

```json
[
  {
    // File data from "Get a file"
    "file_id": "BAADBAADrwADBREAAUZYNjM4ue8ABI",
    "file_path": "voice/file_123.ogg"
  },
  {
    // Message data from trigger  
    "message": {
      "voice": { "file_id": "...", "duration": 5 },
      "from": { "id": 123, "username": "user" }
    }
  }
]
```

## 🎯 Most Likely Fix

Change Merge node **Mode** from "Keep Key Matches" to **"Append"**
