import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../models/system_status.dart';
import '../models/project_model.dart';
import '../services/api_service.dart';

class AgentController extends ChangeNotifier {
    final ApiService _apiService = ApiService();

    List<ChatMessage> messages = [];
    List<MultimodalAttachment> pendingAttachments = [];
    List<ProjectModel> projects = [];
    ProjectModel? currentProject;

    bool isLoggedIn = false;
    String currentUsername = 'Developer';
    String currentUserEmail = 'dev@nvoin.ai';

    bool isLoading = false;
    String currentSessionId = 'nvoin_session_01';
    SystemStatus? systemStatus;
    String selectedMode = 'Nvoin Cloud (Gemini / Gemma 31B)';

    AgentController() {
        init();
    }

    Future<void> init() async {
        systemStatus = await _apiService.checkStatus();
        await loadProjects();
        notifyListeners();
    }

    Future<bool> login(String email, String password) async {
        isLoading = true;
        notifyListeners();
        final res = await _apiService.loginUser(email, password);
        isLoading = false;
        if (res['status'] == 'success') {
            isLoggedIn = true;
            final user = res['user'] ?? {};
            currentUsername = user['username'] ?? email.split('@').first;
            currentUserEmail = user['email'] ?? email;
            notifyListeners();
            return true;
        }
        notifyListeners();
        return false;
    }

    Future<bool> register(String username, String email, String password) async {
        isLoading = true;
        notifyListeners();
        final res = await _apiService.registerUser(username, email, password);
        isLoading = false;
        if (res['status'] == 'success') {
            isLoggedIn = true;
            final user = res['user'] ?? {};
            currentUsername = user['username'] ?? username;
            currentUserEmail = user['email'] ?? email;
            notifyListeners();
            return true;
        }
        notifyListeners();
        return false;
    }

    void logout() {
        isLoggedIn = false;
        messages.clear();
        notifyListeners();
    }

    Future<void> loadProjects() async {
        final list = await _apiService.fetchProjects();
        projects = list.map((item) => ProjectModel.fromJson(item as Map<String, dynamic>)).toList();
        if (projects.isNotEmpty && currentProject == null) {
            currentProject = projects.first;
        }
        notifyListeners();
    }

    Future<void> createAndSelectProject(String name, String path, String os) async {
        final res = await _apiService.createProject(name, path, os);
        final newProj = ProjectModel.fromJson(res);
        projects.add(newProj);
        currentProject = newProj;
        messages.clear();
        notifyListeners();
    }

    void selectProject(ProjectModel proj) {
        currentProject = proj;
        messages.clear();
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
            projectId: currentProject?.id,
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
            confidenceScore: (res['confidence_score'] as num?)?.toDouble() ?? 1.0,
            requiresClarification: res['requires_clarification'] as bool? ?? false,
            implementationPlan: res['implementation_plan'] as String?,
        );

        messages.add(aiMsg);
        isLoading = false;
        notifyListeners();
    }
}
