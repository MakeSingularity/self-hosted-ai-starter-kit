# Oliver Voice Integration - n8n Node Setup Guide

## Quick Reference: Required n8n Nodes

### 1. **Switch Node** (replaces "Detect Message Type")

- **Purpose**: Route different message types
- **Location**: After Telegram Trigger
- **Settings**: 3 rules for voice/audio/text

### 2. **Set Nodes** (for data preparation)

- **Purpose**: Standardize data format for each route
- **Location**: After each Switch output
- **Count**: 2-3 nodes (voice, audio optional, text)

### 3. **Get Audio Node** (NEW - Download Telegram Audio)

- **Purpose**: Download actual audio files from Telegram
- **Location**: After voice/audio Set nodes, before HTTP Request
- **Type**: Telegram node or HTTP Request to Telegram Bot API

### 4. **HTTP Request Node** (for Whisper API)

- **Purpose**: Transcribe downloaded audio files
- **Location**: After Get Audio node
- **URL**: `http://localhost:8000/transcribe/file` (file upload endpoint)

### 4. **Merge Node** (combine paths)

- **Purpose**: Join voice and text processing paths
- **Location**: Before Oliver AI processing
- **Mode**: "Merge By Position"

### 5. **Function Node** (process final message)

- **Purpose**: Extract text for Oliver
- **Location**: After Merge node
- **Output**: Standardized message format

## Step-by-Step Node Configuration

### Node 1: Switch - "Message Type Router"

```
Telegram Trigger → Switch Node
```

**Configuration:**

- **Data Type**: Object
- **Property Name**: `message`
- **Rules**:
  1. `voice` (Object Key Exists) → Output 1
  2. `audio` (Object Key Exists) → Output 2  
  3. `text` (Object Key Exists) → Output 3

### Node 2a: HTTP Request - "Check Whisper API Health" (NEW - Before Voice Processing)

```
Switch (Voice Output) → HTTP Request (Health Check) → IF Node → Telegram Get File
```

**Configuration:**

- **Method**: GET
- **URL**: `http://host.docker.internal:8000/status`
- **Authentication**: None
- **Ignore SSL Issues**: Yes
- **Response**:
  - Success: Continue to file download
  - Error: Log error and use fallback

### Node 2b: IF Node - "API Health Gate"

```
HTTP Request (Health Check) → IF Node
```

**Configuration:**

- **Condition**: `{{ $json.whisper_ready === true }}`
- **True Output**: Continue to Telegram Get File
- **False Output**: Go to error handling or text fallback

## 🔧 **Alternative: n8n-Only Solution (No External Scripts)**

Since n8n blocks `child_process`, use this approach instead:

### **Method 1: Simple Health Check + Graceful Fallback**

```
Telegram Trigger → Switch → HTTP Request (Health Check) → IF Node → Continue or Fallback
```

**HTTP Request - Whisper Health Check:**

- **Method**: GET  
- **URL**: `http://host.docker.internal:8000/`
- **Continue on Fail**: Yes
- **Response**: If success, API is running

**IF Node - API Available Check:**

- **Condition**: `{{ $json.status === "running" }}`
- **True**: Continue with voice transcription
- **False**: Send "Voice transcription unavailable" message

### **Method 2: Start API via Write File + Webhook**

**Write File Node - Create Start Script:**

```javascript
// Generate a simple start command file
const startScript = `cd "C:\\AI Projects\\self-hosted-ai-starter-kit"
.venv\\Scripts\\python.exe scripts\\whisper_service_manager.py start`;

return [{
  json: {
    script_content: startScript,
    file_name: "start_whisper.bat"
  }
}];
```

**Write to**: `C:\\AI Projects\\self-hosted-ai-starter-kit\\temp\\start_whisper.bat`

### **Method 3: Use Execute Command Node (if available)**

Some n8n installations have an "Execute Command" node:

- **Command**: `C:\\AI Projects\\self-hosted-ai-starter-kit\\.venv\\Scripts\\python.exe`
- **Arguments**: `scripts/whisper_service_manager.py start`
- **Working Directory**: `C:\\AI Projects\\self-hosted-ai-starter-kit`

```
Telegram Get File → Set Node
```

**Values to Set:**

- `message_type`: `voice`
- `needs_transcription`: `true`
- `file_id`: `{{ $input.first().json.message.voice.file_id }}` (from original Telegram data)
- `duration`: `{{ $input.first().json.message.voice.duration }}`
- `original_message`: `{{ $input.first().json.message }}`
- `user_id`: `{{ $input.first().json.message.from.id }}`
- `username`: `{{ $input.first().json.message.from.username }}`
- `chat_id`: `{{ $input.first().json.message.chat.id }}`
- `downloaded_file`: `true` (flag to indicate we have binary data)

**🎯 Important**: The Telegram Get File node changes the data structure, so use `$input.first().json` to access the original Telegram message data.

### Node 2b: Set - "Prepare Audio Data"

```
Switch Output 2 → Set Node
```

**Values to Set:**

- `message_type`: `audio`
- `needs_transcription`: `true`
- `file_id`: `{{ $json.message.audio.file_id }}`
- `duration`: `{{ $json.message.audio.duration }}`
- `mime_type`: `{{ $json.message.audio.mime_type }}`
- `original_message`: `{{ $json.message }}`

### Node 2c: Set - "Prepare Text Data"

```
Switch Output 3 → Set Node
```

**Values to Set:**

- `message_type`: `text`
- `needs_transcription`: `false`
- `processed_text`: `{{ $json.message.text }}`
- `original_message`: `{{ $json.message }}`

### Node 3: Telegram Get File - "Download Audio File" ✅ **IMPLEMENTED**

```
Switch (Voice Output) → Telegram Get File → Prepare Voice Data
```

**Configuration for "Telegram - Get a file" node:**

- **Resource**: Message
- **Operation**: Get File
- **File ID**: `{{ $json.message.voice.file_id }}` (for voice messages)
- **Alternative**: `{{ $json.message.audio.file_id }}` (for audio messages)

**🎯 Key Settings:**

- **File ID Source**: Use the file_id from the Switch node output
- **Binary Property**: `data` (this creates `$binary.data` for next node)
- **Keep Binary Data**: Yes

**💡 Pro Tip**: This node downloads the actual audio file and stores it as binary data that can be uploaded directly to Whisper API.

### Node 4: Set - "Prepare Voice Data with Binary"

```
Prepare Voice Data → HTTP Request Node
Prepare Audio Data → HTTP Request Node (same endpoint)
```

**🎯 RECOMMENDED: Use File Upload Method**

**Configuration (for downloaded audio files):**

- **Method**: POST
- **URL**: `http://host.docker.internal:8000/transcribe/file` ✅ **FILE UPLOAD ENDPOINT**
- **Authentication**: None
- **Send Query Parameters**: No
- **Send Headers**: No (multipart/form-data auto-set)
- **Send Body**: Yes
- **Body Content Type**: Form-Data (multipart/form-data)
- **Body Parameters**:

  ```
  Name: file
  Value: {{ $binary.data }} (UNDEFINED - SEE FIX BELOW)
  Type: File
  ```

**🚨 CRITICAL: Fix Binary Data Access**

**Problem**: `={{ $binary.data }}` returns undefined.

**Solution - Debug Binary Data First:**

Add a Debug Function Node after "Telegram Get File":

```javascript
// Debug binary data structure
console.log("🔍 BINARY DEBUG:");
console.log("Binary keys:", Object.keys($binary || {}));
console.log("Available binary properties:");
if ($binary) {
  Object.keys($binary).forEach(key => {
    console.log(`- ${key}:`, typeof $binary[key]);
  });
}

console.log("\n📄 JSON DEBUG:");
console.log("JSON keys:", Object.keys($json));

return [{ 
  json: { 
    ...($json || {}),
    debug_binary_keys: Object.keys($binary || {}),
    has_binary_data: !!$binary
  }, 
  binary: $binary 
}];
```

**Once you find the correct binary property name, update HTTP Request:**

**Common Binary Property Names:**

- `{{ $binary.data }}` (standard)
- `{{ $binary.file }}` (some nodes)
- `{{ $binary.attachment }}` (email/file nodes)
- `{{ $binary.download }}` (download nodes)

**HTTP Request Value**: Use the correct binary property from debug output

**🔧 FALLBACK: Original JSON Method (if file download fails)**

**Configuration:**

- **Method**: POST
- **URL**: `http://host.docker.internal:8000/transcribe/n8n` ✅ **CONFIRMED WORKING**
- **Authentication**: None
- **Send Query Parameters**: No
- **Send Headers**: Yes
- **Headers**:

  ```
  Name: Content-Type
  Value: application/json
  ```

- **Send Body**: Yes
- **Body Content Type**: JSON
- **Body (JSON format)**:

  ```json
  {
    "message": {{ $json.original_message }},
    "message_type": "{{ $json.message_type }}",
    "file_id": "{{ $json.file_id }}",
    "duration": {{ $json.duration }}
  }
  ```

**🚨 IMPORTANT: n8n JSON Body Formatting**

If you get "JSON parameter needs to be valid JSON" error, use this **Alternative Method**:

**Method 1: Use Expression Editor (Recommended)**

- **Body Content Type**: Raw/Text
- **Body**: Click the "Expression" tab and use:

  ```javascript
  {{ JSON.stringify({
    message: $json.original_message,
    message_type: $json.message_type,
    file_id: $json.file_id,
    duration: $json.duration
  }) }}
  ```

**Method 2: Use Individual Fields in JSON Editor**

- **Body Content Type**: JSON
- Click "Add Field" for each property:
  - Key: `message`, Value: `{{ $json.original_message }}` (no quotes)
  - Key: `message_type`, Value: `{{ $json.message_type }}` (with quotes)
  - Key: `file_id`, Value: `{{ $json.file_id }}` (with quotes)  
  - Key: `duration`, Value: `{{ $json.duration }}` (no quotes)

## � CRITICAL FIX: Transcribe Node Returning Null Items

**Problem**: HTTP Request node sends `{'': ''}` to Whisper API, causing null responses.

**Root Cause**: The Set nodes aren't capturing Telegram data correctly, so `original_message` is null.

**🔧 IMMEDIATE SOLUTION:**

### Step 1: Fix Set Node Configuration

**For Voice Messages Set Node:**

```
Values to Set:
- original_message: {{ $json }}
- message_type: voice
- needs_transcription: true
- file_id: {{ $json.message.voice.file_id }}
- duration: {{ $json.message.voice.duration }}
- user_id: {{ $json.message.from.id }}
- username: {{ $json.message.from.username }}
- chat_id: {{ $json.message.chat.id }}
- telegram_message: {{ $json.message }}
```

**For Text Messages Set Node:**

```
Values to Set:
- original_message: {{ $json }}
- message_type: text
- needs_transcription: false
- processed_text: {{ $json.message.text }}
- user_id: {{ $json.message.from.id }}
- username: {{ $json.message.from.username }}
- chat_id: {{ $json.message.chat.id }}
- telegram_message: {{ $json.message }}
```

### Step 2: Fix HTTP Request Node JSON Body

**🎯 Use Method 3: Simple Fixed Values (Most Reliable)**

**Body Content Type**: JSON
**Body Format**:

```json
{
  "message": {
    "voice": {
      "file_id": "test_file_id",
      "duration": 5
    },
    "from": {
      "id": 12345,
      "username": "testuser"
    },
    "chat": {
      "id": 67890
    }
  },
  "message_type": "voice",
  "file_id": "test_file_id",
  "duration": 5
}
```

**Replace with your actual values:**

- Change `test_file_id` to `{{ $json.file_id }}`
- Change `12345` to `{{ $json.user_id }}`
- Change `67890` to `{{ $json.chat_id }}`
- Change `5` to `{{ $json.duration }}`

**🔧 Alternative: Use Expression Method**

**Body Content Type**: Raw/Text
**Body** (Click Expression tab):

```javascript
{{ JSON.stringify({
  message: {
    voice: {
      file_id: $json.file_id || "test_file",
      duration: $json.duration || 3
    },
    from: {
      id: $json.user_id || 12345,
      username: $json.username || "user"
    },
    chat: {
      id: $json.chat_id || 67890
    }
  },
  message_type: $json.message_type || "voice",
  file_id: $json.file_id || "test_file",
  duration: $json.duration || 3
}) }}
```

### Step 3: Debug the Data Flow

**Add Debug Function Node before HTTP Request:**

```javascript
// Debug what data the Set node is sending
console.log("🔍 DEBUG: Data before HTTP Request");
console.log("Keys available:", Object.keys($json));
console.log("Full data:", JSON.stringify($json, null, 2));

console.log("Required fields:");
console.log("- file_id:", $json.file_id);
console.log("- duration:", $json.duration);
console.log("- user_id:", $json.user_id);
console.log("- original_message:", !!$json.original_message);

return [{ json: $json }];
```

### Step 4: Test with Fixed Data First

**Before using dynamic data, test with static values:**

**HTTP Request Body (Static Test)**:

```json
{
  "message": {
    "voice": {
      "file_id": "static_test_123",
      "duration": 5
    },
    "from": {
      "id": 12345,
      "username": "testuser"
    },
    "chat": {
      "id": 67890
    }
  },
  "message_type": "voice",
  "file_id": "static_test_123",
  "duration": 5
}
```

If this works, then gradually replace with expressions:

- `"static_test_123"` → `"{{ $json.file_id }}"`
- `5` → `{{ $json.duration }}`
- etc.

**Alternative if using Expression (Raw/Text body type):**

- **Body Content Type**: Raw/Text
- **Body**:

  ```javascript
  {{ JSON.stringify({
    message: $json.original_message,
    message_type: $json.message_type,
    file_id: $json.file_id,
    duration: $json.duration
  }) }}
  ```

**🔧 Debugging the Error:**
If you're still getting `'str' object has no attribute 'get'`:

1. **Check your HTTP Request body format** - don't put quotes around object fields
2. **Test with a simple body first**:

   ```json
   {
     "message": {
       "voice": {
         "file_id": "test123",
         "duration": 5
       }
     }
   }
   ```

3. **Verify the Whisper API endpoint** by testing it directly:

   ```powershell
   $body = @{
     message = @{
       voice = @{
         file_id = "test123"
         duration = 5
       }
     }
   } | ConvertTo-Json -Depth 3
   
   Invoke-RestMethod -Uri "http://localhost:8000/transcribe/n8n" -Method POST -Body $body -ContentType "application/json"
   ```

### Node 4: NO MERGE NEEDED - Direct Connections

```
🚨 IMPORTANT: Don't use a Merge node - it causes text-only messages to hang!

CORRECT WORKFLOW STRUCTURE:
Voice/Audio: Switch → Set → HTTP Request → Function → AI Agent
Text: Switch → Set → Function → AI Agent
```

**🔧 SOLUTION: Remove Merge Node Completely**

**Why Merge Fails:**

- Merge waits for input from ALL connected paths
- Text messages don't go through HTTP Request (voice path)
- Merge waits forever for the missing voice input
- Result: Text messages never reach the AI Agent

**Correct Configuration:**

1. **Voice/Audio Path**: Switch → Prepare Voice Data → Transcribe Voice Message → Process Message Content → AI Agent
2. **Text Path**: Switch → Prepare Text Data → Process Message Content → AI Agent

**Connect Multiple Inputs to Function Node:**

- The "Process Message Content" Function node can accept inputs from BOTH:
  - HTTP Request node (voice transcription results)
  - Set node (text message data)
- n8n will execute the Function node whenever ANY input arrives
- No merge required!

**Alternative If You Must Use Merge:**

**Option A: Use "Wait" node with "Wait for any input"**

- Change to **Wait** node
- **Mode**: "Wait for any input to arrive" (NOT "Wait for all")
- **Max items**: 1
- This processes whichever arrives first

**Option B: Use separate workflows**

- Create separate workflows for voice and text
- Use webhooks or triggers to call each other

**Option C: Use IF node instead of merge**

- Add IF node after each path
- Condition: Check if data exists
- Both paths connect to same Function node

### Node 5: Function - "Process Message Content"

```
Merge Node → Function Node
```

**JavaScript Code (Enhanced for Robust Data Access):**

```javascript
// Process message content with robust data access for Oliver workflow
// Handles both voice transcription and text message data flows

const allItems = items; // Get all input data
let currentItem = items[0].json;

// Debug logging - shows exactly what data we're receiving
console.log("🔍 FUNCTION NODE DEBUG:");
console.log("Total items received:", allItems.length);
console.log("Current item keys:", Object.keys(currentItem));
console.log("Full item data:", JSON.stringify(currentItem, null, 2));

let messageText = '';
let messageSource = '';
let originalMessage = null;
let telegramData = null;

// Strategy 1: Look for original_message in current item (from Whisper API response)
if (currentItem.original_message) {
  originalMessage = currentItem.original_message;
  console.log("✅ Found original_message in current item");
} 

// Strategy 2: Check if current item IS the original Telegram message
else if (currentItem.message && currentItem.message.from) {
  originalMessage = currentItem;
  console.log("✅ Current item appears to be the original Telegram message");
}

// Strategy 3: Search through all items from merge node
else {
  console.log("🔍 Searching through all items for Telegram data...");
  for (let i = 0; i < allItems.length; i++) {
    const item = allItems[i].json;
    console.log(`Item ${i} keys:`, Object.keys(item));
    
    // Look for Telegram message structure
    if (item.message && item.message.from) {
      originalMessage = item;
      console.log(`✅ Found Telegram message in item ${i}`);
      break;
    }
    
    // Look for original_message field
    if (item.original_message) {
      originalMessage = item.original_message;
      console.log(`✅ Found original_message field in item ${i}`);
      break;
    }
  }
}

// Extract the actual Telegram message object
if (originalMessage && originalMessage.message) {
  telegramData = originalMessage.message;
} else if (originalMessage && originalMessage.from) {
  telegramData = originalMessage;
} else {
  console.log("❌ Could not find Telegram message structure");
  telegramData = currentItem.message || {};
}

// Determine message text and source
if (currentItem.needs_transcription !== false && currentItem.transcription) {
  // Voice/Audio message with transcription
  messageText = currentItem.transcription.text || "Transcription failed";
  messageSource = `voice_message (${currentItem.message_type || 'voice'})`;
  
  if (currentItem.transcription.duration) {
    messageSource += ` (${currentItem.transcription.duration}s)`;
  }
  
  if (currentItem.transcription.confidence) {
    messageSource += ` [confidence: ${Math.round(currentItem.transcription.confidence * 100)}%]`;
  }
  
  console.log("📢 Using transcribed voice message");
} else {
  // Text message
  messageText = currentItem.processed_text || 
               telegramData?.text || 
               currentItem.text || 
               'No text found';
  messageSource = 'text_message';
  console.log("📝 Using text message");
}

// Extract user information with multiple fallback strategies
const userId = telegramData?.from?.id || 
               originalMessage?.from?.id || 
               currentItem.user_id || 
               'unknown_user';

const username = telegramData?.from?.username || 
                 telegramData?.from?.first_name || 
                 originalMessage?.from?.username || 
                 originalMessage?.from?.first_name || 
                 currentItem.username || 
                 'unknown_user';

const chatId = telegramData?.chat?.id || 
               originalMessage?.chat?.id || 
               telegramData?.from?.id ||
               originalMessage?.from?.id ||
               currentItem.chat_id || 
               'unknown_chat';

const firstName = telegramData?.from?.first_name || 
                  originalMessage?.from?.first_name || 
                  currentItem.first_name || 
                  '';

const lastName = telegramData?.from?.last_name || 
                 originalMessage?.from?.last_name || 
                 currentItem.last_name || 
                 '';

// Create comprehensive output for Oliver
console.log("📤 OUTPUT DATA:");
console.log(`User ID: ${userId}, Username: ${username}, Chat ID: ${chatId}`);
console.log(`Message: "${messageText}" (Source: ${messageSource})`);

return [{
  json: {
    processed_text: messageText,
    message_source: messageSource,
    user_id: userId,
    username: username,
    first_name: firstName,
    last_name: lastName,
    chat_id: chatId,
    timestamp: new Date().toISOString(),
    
    // Additional context for Oliver
    is_voice_message: messageSource.includes('voice'),
    message_length: messageText.length,
    
    // Debugging information (remove in production)
    debug: {
      total_items_received: allItems.length,
      found_original_message: !!originalMessage,
      found_telegram_data: !!telegramData,
      current_item_keys: Object.keys(currentItem),
      has_transcription: !!currentItem.transcription
    }
  }
}];
```

### Node 6: AI Agent - "Oliver AI Response" (Recommended)

```
Function Node → AI Agent Node
```

**Configuration:**

- **Node Type**: AI Agent
- **Chat Model**: Ollama Chat Model
- **Base URL**: `http://ollama:11434` (or `http://host.docker.internal:11434` if needed)
- **Model**: `llama3.1:latest`
- **System Message**:

  ```
  You are Oliver, a helpful AI assistant. 
  
  When responding to voice messages, acknowledge that you heard their voice message. If the transcription seems unclear, politely ask for clarification.
  
  Current message source: {{ $json.message_source }}
  ```

- **Prompt**: `{{ $json.processed_text }}`
- **Options**:
  - **Temperature**: 0.7
  - **Max Tokens**: 1000
- **Output Parser**: (Optional) Simple text output

**Alternative: Manual HTTP Request** (if AI Agent node not available)

- **Method**: POST
- **URL**: `http://ollama:11434/api/generate`
- **Headers**: `Content-Type: application/json`
- **Body**:

  ```json
  {
    "model": "llama3.1:latest",
    "prompt": "{{ $json.processed_text }}",
    "stream": false,
    "system": "You are Oliver, a helpful AI assistant..."
  }
  ```

### Node 7: Set - "Format Response" (if using AI Agent)

```
AI Agent → Set Node
```

**Values to Set:**

- `response`: `{{ $json.output }}` (from AI Agent)
- `chat_id`: `{{ $input.first().json.chat_id }}`
- `message_type`: `{{ $input.first().json.message_source }}`

**Alternative: Function Node - "Extract Response" (if using HTTP Request)**

```
HTTP Request → Function Node
```

**JavaScript Code:**

```javascript
return [{
  json: {
    response: $json.response,
    chat_id: $input.first().json.chat_id
  }
}];
```

### Node 8: HTTP Request - "Send Telegram Response" (existing)

```
Extract Response → HTTP Request Node (Telegram)
```

**Configuration:** (Keep your existing Telegram send message setup)

## Complete Workflow Path

**🎯 UPDATED WORKFLOW WITH AUDIO DOWNLOAD:**

```
Telegram Trigger
    ↓
Switch (Message Type Router)
    ├── Voice → Set (Prepare Voice) → Get Audio → HTTP (Whisper File API) ──┐
    ├── Audio → Set (Prepare Audio) → Get Audio → HTTP (Whisper File API) ──┤
    └── Text → Set (Prepare Text) ─────────────────────────────────────────────┘
                                                                              ↓
                                                                      Function (Process Message)
                                                                              ↓
                                                                  AI Agent (Oliver Response)
                                                                              ↓
                                                                  Set (Format Response)
                                                                              ↓
                                                                  HTTP (Send Telegram Reply)
```

**🔧 KEY IMPROVEMENT: No Merge Node Needed!**

- Voice/Audio path: Downloads actual file and transcribes it
- Text path: Goes directly to Function node
- Function node handles both inputs automatically
- No hanging on text-only messages

**📱 Alternative: Telegram Trigger with Auto-Download**

If your Telegram Trigger has built-in file download:

```
Telegram Trigger (Download Files: Yes)
    ↓
Switch (Message Type Router)
    ├── Voice/Audio → Set (Prepare) → HTTP (Whisper File API) ──┐
    └── Text → Set (Prepare Text) ────────────────────────────────┘
                                                                  ↓
                                                          Function (Process Message)
                                                                  ↓
                                                      AI Agent (Oliver Response)
```

**Key Point**: Both Voice and Audio messages use the **same HTTP Request node** for transcription. You can either:

**Option A: Single HTTP Request Node (Recommended)**

- Connect both "Prepare Voice Data" and "Prepare Audio Data" to the same "Transcribe Voice Message" node
- The Whisper API handles both voice and audio formats

**Option B: Separate HTTP Request Nodes**

- Create separate "Transcribe Voice" and "Transcribe Audio" nodes if you want different processing
- Both would use the same URL and configuration

## Testing Your Setup

### 1. **Text Message Test**

- Send: "Hello Oliver"
- Path: Telegram → Switch → Set (Text) → Merge → Function → Oliver AI
- Expected: Normal Oliver response

### 2. **Voice Message Test**  

- Send: Voice recording saying "What's the weather?"
- Path: Telegram → Switch → Set (Voice) → HTTP (Whisper) → Merge → Function → Oliver AI
- Expected: "I heard your voice message asking about the weather..."

### 3. **Error Handling Test**

- Send: Very unclear voice message
- Expected: Polite request to clarify or resend as text

## Common n8n Setup Issues

### Switch Node Not Working

- ✅ Check "Data Type" is set to "Object"
- ✅ Property name is exactly `message`
- ✅ Rules use "Object Key Exists" operation

### HTTP Request Fails

- ✅ Ensure Whisper API is running: `http://localhost:8000`
- ✅ Check request body uses `{{ JSON.stringify($json) }}`
- ✅ Verify Content-Type header is set

### Merge Node Issues

- ✅ Use "Merge By Position" mode
- ✅ Connect voice path to Input 1, text path to Input 2
- ✅ Check both paths actually reach the merge node

### Function Node Errors

- ✅ Test with simple `return [{ json: $json }]` first
- ✅ Check for typos in property names
- ✅ Use browser dev tools to debug JavaScript
- ✅ **NEW**: Check for null `original_message` in Function node

**Debugging "original_message" null errors:**

1. **Add debug Function node before Process Message Content:**

   ```javascript
   // Debug what data we're getting
   console.log("Merge output:", JSON.stringify($json, null, 2));
   return [{ json: $json }];
   ```

2. **Check Set node outputs:**
   - Verify "Prepare Voice Data" sets `original_message` correctly
   - Verify "Prepare Text Data" sets `original_message` correctly

3. **Check HTTP Request response:**
   - Whisper API might be overwriting the data structure
   - Check if `original_message` survives the HTTP request

4. **Alternative data access patterns:**

   ```javascript
   // Try these if original_message is null:
   const message = item.original_message || item.message || item.body?.message;
   const userId = message?.from?.id || item.user_id;
   const chatId = message?.chat?.id || item.chat_id;
   ```

5. **🚨 CRITICAL FIX: Merge Node Data Loss**

   **Problem**: The Merge node can lose the `original_message` data when combining voice and text paths.

   **Solution A: Use "Wait" Node Instead of Merge**
   - Replace the Merge node with a **Wait** node
   - Set mode to "Wait for all incoming data"
   - This preserves data structure better

   **Solution B: Modify Set Nodes to Include More Data**
   Update your Set nodes to include ALL Telegram data:

   **For Voice Messages (Set Node):**

   ```
   message_type: voice
   needs_transcription: true
   file_id: {{ $json.message.voice.file_id }}
   duration: {{ $json.message.voice.duration }}
   original_message: {{ $json.message }}
   user_id: {{ $json.message.from.id }}
   username: {{ $json.message.from.username }}
   first_name: {{ $json.message.from.first_name }}
   chat_id: {{ $json.message.chat.id }}
   telegram_message_id: {{ $json.message.message_id }}
   ```

   **For Text Messages (Set Node):**

   ```
   message_type: text
   needs_transcription: false
   processed_text: {{ $json.message.text }}
   original_message: {{ $json.message }}
   user_id: {{ $json.message.from.id }}
   username: {{ $json.message.from.username }}
   first_name: {{ $json.message.from.first_name }}
   chat_id: {{ $json.message.chat.id }}
   telegram_message_id: {{ $json.message.message_id }}
   ```

   **Solution C: Enhanced Function Node (Recommended)**
   Use the enhanced Function node code above that searches through ALL items from the merge to find the Telegram data.

6. **Quick Test**: Add this debug Function node right after your Telegram Trigger:

   ```javascript
   // Debug Telegram data structure
   console.log("🔍 RAW TELEGRAM DATA:");
   console.log("Keys:", Object.keys($json));
   console.log("Full data:", JSON.stringify($json, null, 2));
   
   if ($json.message) {
     console.log("Message keys:", Object.keys($json.message));
     console.log("From data:", $json.message.from);
     console.log("Chat data:", $json.message.chat);
   }
   
   return [{ json: $json }];
   ```

   This will show you exactly what data structure Telegram is sending.

## Quick Verification Commands

```powershell
# Check Whisper API is running
Invoke-RestMethod -Uri "http://localhost:8000/status" -Method GET

# Check Oliver workflow
# Send test message in Telegram

# Monitor n8n logs
docker logs n8n | findstr -i error

# Check all containers
docker ps | findstr -E "(n8n|ollama|whisper)"
```
