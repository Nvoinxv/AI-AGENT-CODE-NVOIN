import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../models/system_status.dart';
import '../services/api_service.dart';

class AgentController extends ChangeNotifier {
    final ApiService _apiService = ApiService();

    List<ChatMessage> messages = [];
    List<MultimodalAttachment> pendingAttachments = [];
    bool isLoading = false;
    String currentSessionId = 'nvoin_session_01';
    SystemStatus? systemStatus;
    String selectedMode = 'Nvoin v4.2 (Gemma 12B)';

    AgentController() {
        init();
    }

    Future<void> init() async {
        systemStatus = await _apiService.checkStatus();
        notifyListeners();
    }

    void addAttachment(String type, String content) {
        pendingAttachments.add(MultimodalAttachment(type: type, content: content));
        notifyListeners();
    }

    void removeAttachment(int index) {
        if (index >= 0 && index < pendingAttachments.length) {
            pendingAttachments.removeAt(index);
            notifyListeners();
        }
    }

    void setMode(String mode) {
        selectedMode = mode;
        notifyListeners();
    }

    void startNewChat() {
        messages.clear();
        pendingAttachments.clear();
        currentSessionId = 'nvoin_${DateTime.now().millisecondsSinceEpoch}';
        notifyListeners();
    }

    Future<void> sendPrompt(String text) async {
        if (text.trim().isEmpty && pendingAttachments.isEmpty) return;

        final userMsg = ChatMessage(
            id: DateTime.now().toString(),
            role: MessageRole.user,
            content: text,
            timestamp: DateTime.now(),
            attachments: List.from(pendingAttachments),
        );

        messages.add(userMsg);
        final attachmentsToSend = List<MultimodalAttachment>.from(pendingAttachments);
        pendingAttachments.clear();
        isLoading = true;
        notifyListeners();

        final res = await _apiService.sendChatMessage(
            prompt: text,
            sessionId: currentSessionId,
            attachments: attachmentsToSend,
            mode: selectedMode,
        );

        final subagentListRaw = res['subagent_logs'] as List<dynamic>? ?? [];
        final subagentLogs = subagentListRaw
            .map((item) => SubagentLog.fromJson(item as Map<String, dynamic>))
            .toList();

        final aiMsg = ChatMessage(
            id: DateTime.now().toString(),
            role: MessageRole.assistant,
            content: res['response'] ?? 'Kesalahan menerima respons.',
            timestamp: DateTime.now(),
            subagentLogs: subagentLogs,
        );

        messages.add(aiMsg);
        isLoading = false;
        notifyListeners();
    }
}
