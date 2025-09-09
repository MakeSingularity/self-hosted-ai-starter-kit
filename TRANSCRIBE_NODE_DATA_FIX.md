# 🚨 URGENT: Fix "Transcribe Voice Message" Data Mapping

## Problem: Audio File Not Reaching Whisper API

The "Transcribe Voice Message" node is sending message metadata but NOT the actual audio file data.

## 🎯 Two Solutions Available

### **SOLUTION 1: Use File Upload (Recommended)**

**Change "Transcribe Voice Message" node to upload the actual file:**

1. **URL**: `http://host.docker.internal:8000/transcribe/file`
2. **Method**: `POST`
3. **Body Type**: `Form-Data` (NOT JSON)
4. **Form Fields**:

   ```
   file: {{ $binary.data }}
   ```

### **SOLUTION 2: Use n8n Endpoint with Proper Data**

**Keep current URL but fix the data mapping:**

1. **URL**: `http://host.docker.internal:8000/transcribe/n8n`
2. **Method**: `POST`
3. **Body Type**: `JSON`
4. **JSON Body**:

   ```json
   {
     "message": {
       "voice": {
         "file_id": "{{ $json.file_id }}",
         "duration": "{{ $json.duration }}",
         "file_unique_id": "{{ $json.file_unique_id }}"
       },
       "from": {
         "id": "{{ $('Telegram Trigger').first().json.message.from.id }}",
         "username": "{{ $('Telegram Trigger').first().json.message.from.username }}"
       }
     }
   }
   ```

## 🔍 Current Issue Analysis

The node is probably sending something like:

```json
{
  "message": {
    "text": "some text"
  }
}
```

Instead of:

```json
{
  "message": {
    "voice": {
      "file_id": "actual_telegram_file_id",
      "duration": 5
    }
  }
}
```

## ✅ Recommended Fix (Solution 1)

**Use the file upload endpoint since you already have the file downloaded:**

1. Change URL to: `http://host.docker.internal:8000/transcribe/file`
2. Change Body Type to: `Form-Data`
3. Add form field: `file = {{ $binary.data }}`

This will upload the actual audio file for transcription.

## 🧪 Test Your Fix

After making changes, send a voice message and check:

1. Does the node execute successfully?
2. Does it return actual transcribed text?
3. Check Fast Whisper API logs for file processing

## 🔧 Debug Current Data

To see what data your node is currently sending:

1. Change URL temporarily to: `http://host.docker.internal:8000/debug/request`
2. Send a voice message
3. Check the response to see actual data format
4. Then fix the mapping and change URL back
