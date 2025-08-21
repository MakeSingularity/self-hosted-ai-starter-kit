// Simplified Oliver Message Processor - Fixed Version
// Handles voice and text messages with proper error handling

try {
    console.log('🔄 Oliver: Processing message...');

    // Get input data safely
    const currentItem = $input.item.json;
    console.log('📥 Input keys:', Object.keys(currentItem));

    // Initialize output data
    let outputData = {
        processed_text: '',
        message_source: 'unknown',
        user_data: {},
        timestamp: new Date().toISOString(),
        debug_info: {
            input_keys: Object.keys(currentItem),
            processing_path: 'unknown'
        }
    };

    // Extract user information (with safe fallbacks)
    const extractUserData = (source) => {
        if (!source) return {};

        const fromData = source.from || source.user_data || {};
        return {
            user_id: fromData.id || fromData.user_id || 'unknown',
            username: fromData.username || fromData.first_name || 'unknown',
            first_name: fromData.first_name || '',
            last_name: fromData.last_name || '',
            chat_id: source.chat?.id || fromData.id || 'unknown'
        };
    };

    // CASE 1: Voice/Audio Message with Transcription
    if (currentItem.transcription && currentItem.transcription.text) {
        console.log('🎤 Processing transcribed voice message');

        outputData.processed_text = currentItem.transcription.text;
        outputData.message_source = `voice_transcribed (${currentItem.message_type || 'voice'})`;
        outputData.user_data = extractUserData(currentItem.original_message || currentItem);
        outputData.debug_info.processing_path = 'voice_transcription';

        if (currentItem.transcription.confidence) {
            outputData.transcription_confidence = currentItem.transcription.confidence;
        }
    }

    // CASE 2: Direct Text Message
    else if (currentItem.processed_text || currentItem.text) {
        console.log('📝 Processing text message');

        outputData.processed_text = currentItem.processed_text || currentItem.text;
        outputData.message_source = 'text_direct';
        outputData.user_data = extractUserData(currentItem.oringal_message || currentItem.original_message || currentItem);
        outputData.debug_info.processing_path = 'text_direct';
    }

    // CASE 3: Telegram Message Structure
    else if (currentItem.message) {
        console.log('📱 Processing Telegram message structure');

        const telegramMsg = currentItem.message;
        outputData.user_data = extractUserData(telegramMsg);
        outputData.debug_info.processing_path = 'telegram_structure';

        if (telegramMsg.text) {
            outputData.processed_text = telegramMsg.text;
            outputData.message_source = 'telegram_text';
        } else if (telegramMsg.voice || telegramMsg.audio) {
            outputData.processed_text = 'Voice message received - transcription may be needed';
            outputData.message_source = telegramMsg.voice ? 'telegram_voice' : 'telegram_audio';
        } else {
            outputData.processed_text = 'Message received - type unknown';
            outputData.message_source = 'telegram_unknown';
        }
    }

    // CASE 4: Fallback - Unknown structure
    else {
        console.log('❓ Unknown message structure - using fallback');

        outputData.processed_text = 'Message received but structure unknown';
        outputData.message_source = 'fallback';
        outputData.user_data = extractUserData(currentItem);
        outputData.debug_info.processing_path = 'fallback';
        outputData.debug_info.available_fields = Object.keys(currentItem);
    }

    // Validate required fields
    if (!outputData.processed_text) {
        outputData.processed_text = 'No message text could be extracted';
    }

    if (!outputData.user_data.user_id || outputData.user_data.user_id === 'unknown') {
        console.log('⚠️ Warning: Could not extract user ID');
        outputData.user_data.user_id = 'anonymous_user';
    }

    console.log('✅ Oliver: Message processed successfully');
    console.log(`📤 Output: "${outputData.processed_text.substring(0, 50)}..." from ${outputData.user_data.username}`);

    return [{
        json: outputData
    }];

} catch (error) {
    console.error('❌ Oliver: Error processing message:', error.message);

    // Return error-safe output
    return [{
        json: {
            processed_text: 'Sorry, I encountered an error processing your message. Please try again.',
            message_source: 'error',
            user_data: {
                user_id: 'error_user',
                username: 'unknown',
                first_name: '',
                last_name: '',
                chat_id: 'unknown'
            },
            timestamp: new Date().toISOString(),
            error_info: {
                message: error.message,
                stack: error.stack
            },
            debug_info: {
                processing_path: 'error_handler'
            }
        }
    }];
}
