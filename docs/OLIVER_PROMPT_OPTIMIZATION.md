# Oliver Prompt Optimization with n8n Prompt Assistant

## 🚨 **Current Issues in Oliver's Prompt**

### **Issue 1: Conflicting Response Formats**
**Problem**: Prompt says "respond with a markdown code snippet of a json blob" but also "send a message in Telegram-supported HTML format"

**Current Problematic Text:**
```
Here is the user's input (remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else):

{{input}}

SYSTEM PROMPT
----------------------
...In your reply, always send a message in Telegram-supported HTML format...
```

### **Issue 2: Typos and Formatting Errors**
**Problems Found:**
- "striketrough" → should be "strikethrough"
- "4gt;" → should be "&gt;"
- "rply" → should be "reply"

### **Issue 3: Overly Complex Structure**
**Problem**: Prompt mixes agent instructions with direct chat instructions

## ✅ **Optimized Prompt with Extension Assistance**

### **Recommended Replacement:**
```
SYSTEM INSTRUCTIONS
You are Oliver, a helpful AI assistant chatting via Telegram.

CONTEXT:
- User: {{ $json.message.from.first_name }}
- Date: {{ DateTime.fromISO($now).toLocaleString(DateTime.DATETIME_FULL) }}
- Input: {{ $json.message.text }}

RESPONSE RULES:
1. Always respond in Telegram HTML format
2. Use formatting appropriately: <b>bold</b>, <i>italic</i>, <code>code</code>
3. Address user by name occasionally
4. Handle Telegram commands (starting with /) appropriately
5. Be helpful and conversational

HTML FORMATTING GUIDE:
- <b>bold text</b> or <strong>bold text</strong>
- <i>italic text</i> or <em>italic text</em>  
- <u>underlined text</u>
- <s>strikethrough text</s>
- <code>inline code</code>
- <pre><code class="language-python">code block</code></pre>
- <a href="url">link text</a>
- <span class="tg-spoiler">spoiler text</span>

IMPORTANT: Replace special characters with HTML entities:
- < with &lt;
- > with &gt;  
- & with &amp; (except in HTML tags)

TELEGRAM COMMANDS:
- /start: Welcome the user and introduce yourself
- /help: Provide assistance information
- Other commands: Respond appropriately based on context
```

## 🛠️ **How to Apply with n8n Prompt Assistant**

### **Step 1: Open Workflow File**
1. Open `workflows_backup/Oliver.json` in VS Code
2. Extension will provide syntax highlighting for the AI Agent node
3. Locate the `systemMessage` parameter (around line 13)

### **Step 2: Use Extension Features**
1. **Syntax Highlighting**: See the prompt structure clearly
2. **Variable Validation**: Ensure `{{ $json.message.text }}` syntax is correct
3. **Template Snippets**: Access AI agent prompt templates
4. **Auto-completion**: Get suggestions for n8n expressions

### **Step 3: Replace System Message**
Replace the current long `systemMessage` with the optimized version above.

### **Step 4: Update in n8n**
1. Copy the optimized workflow to n8n
2. Or use our sync tool: `python scripts/copilot_n8n_tool.py sync`

## 📊 **Before/After Comparison**

### **Before (Issues):**
- ❌ Conflicting JSON/HTML instructions
- ❌ Typos and formatting errors  
- ❌ Overly complex structure
- ❌ Mixed agent/chat paradigms

### **After (With Extension Help):**
- ✅ Clear Telegram HTML focus
- ✅ Corrected typos and formatting
- ✅ Simplified, logical structure
- ✅ Consistent chat bot approach

## 🔍 **Testing the Improvements**

### **Monitor Performance:**
```bash
# Before making changes - establish baseline
python scripts/ai_agent_debugger.py failures Oliver

# Monitor live executions during testing
python scripts/realtime_monitor.py live

# After changes - validate improvements
python scripts/ai_agent_debugger.py prompt Oliver
```

### **What to Expect:**
1. **Clearer Responses**: Oliver should respond more consistently
2. **Better Formatting**: Proper Telegram HTML formatting
3. **Fewer Errors**: No more conflicting instruction confusion
4. **Improved Context**: Better use of user names and commands

## 🚀 **Extension-Specific Benefits**

### **Visual Editing:**
- See prompt structure highlighted in different colors
- Identify variable placeholders easily
- Spot syntax errors visually

### **Smart Assistance:**
- Auto-complete for n8n variables like `{{ $json.message... }}`
- Snippet suggestions for common prompt patterns
- Syntax validation for n8n expressions

### **Template Integration:**
- Access to proven AI agent prompt templates
- Telegram-specific formatting snippets
- Best practice prompt structures

This optimization leverages both the visual capabilities of the n8n Prompt Assistant extension and the analytical power of our monitoring tools for the best possible result!
