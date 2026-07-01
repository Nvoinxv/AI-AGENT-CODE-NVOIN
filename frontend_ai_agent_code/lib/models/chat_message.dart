enum MessageRole { user, assistant, system, subagent }

class MultimodalAttachment {
    final String type; // 'image', 'mention', 'action', 'browser'
    final String content;
    final Map<String, dynamic>? metadata;

    MultimodalAttachment({
        required this.type,
        required this.content,
        this.metadata,
    });

    Map<String, dynamic> toJson() => {
        'type': type,
        'content': content,
        if (metadata != null) 'metadata': metadata,
    };
}

class SubagentLog {
    final String agentName;
    final String taskPrompt;
    final String output;
    final bool success;

    SubagentLog({
        required this.agentName,
        required this.taskPrompt,
        required this.output,
        required this.success,
    });

    factory SubagentLog.fromJson(Map<String, dynamic> json) {
        return SubagentLog(
            agentName: json['agent_name'] ?? 'unknown',
            taskPrompt: json['task_prompt'] ?? '',
            output: json['output'] ?? '',
            success: json['success'] ?? true,
        );
    }
}

class ChatMessage {
    final String id;
    final MessageRole role;
    final String content;
    final DateTime timestamp;
    final List<MultimodalAttachment>? attachments;
    final List<SubagentLog>? subagentLogs;
    final double? confidenceScore;
    final bool? requiresClarification;
    final String? implementationPlan;

    ChatMessage({
        required this.id,
        required this.role,
        required this.content,
        required this.timestamp,
        this.attachments,
        this.subagentLogs,
        this.confidenceScore,
        this.requiresClarification,
        this.implementationPlan,
    });
}
