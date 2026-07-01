import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../../core/constants/app_colors.dart';
import '../../../models/chat_message.dart';

class MessageBubble extends StatelessWidget {
    final ChatMessage message;

    const MessageBubble({super.key, required this.message});

    @override
    Widget build(BuildContext context) {
        final isUser = message.role == MessageRole.user;

        return Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                children: [
                    if (!isUser) ...[
                        Container(
                            width: 32, height: 32,
                            decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: AppColors.heroGradient,
                            ),
                            child: const Icon(LucideIcons.cpu, size: 16, color: Colors.black),
                        ),
                        const SizedBox(width: 12),
                    ],

                    Flexible(
                        child: Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                                color: isUser ? AppColors.primaryNeon.withOpacity(0.15) : AppColors.surfaceCard,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(
                                    color: isUser ? AppColors.primaryNeon.withOpacity(0.4) : AppColors.glassBorder,
                                ),
                            ),
                            child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                    // Confidence Score Badge untuk AI Assistant
                                    if (!isUser && message.confidenceScore != null) ...[
                                        Row(
                                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                            children: [
                                                Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                                    decoration: BoxDecoration(
                                                        color: (message.confidenceScore! >= 0.75)
                                                            ? AppColors.statusSuccess.withOpacity(0.2)
                                                            : AppColors.statusWarning.withOpacity(0.2),
                                                        borderRadius: BorderRadius.circular(12),
                                                        border: Border.all(
                                                            color: (message.confidenceScore! >= 0.75)
                                                                ? AppColors.statusSuccess
                                                                : AppColors.statusWarning,
                                                        ),
                                                    ),
                                                    child: Row(
                                                        mainAxisSize: MainAxisSize.min,
                                                        children: [
                                                            Icon(
                                                                (message.confidenceScore! >= 0.75)
                                                                    ? LucideIcons.shieldCheck
                                                                    : LucideIcons.shieldAlert,
                                                                size: 12,
                                                                color: (message.confidenceScore! >= 0.75)
                                                                    ? AppColors.statusSuccess
                                                                    : AppColors.statusWarning,
                                                            ),
                                                            const SizedBox(width: 5),
                                                            Text(
                                                                'Confidence: ${(message.confidenceScore! * 100).toInt()}%',
                                                                style: TextStyle(
                                                                    fontSize: 10,
                                                                    fontWeight: FontWeight.bold,
                                                                    color: (message.confidenceScore! >= 0.75)
                                                                        ? AppColors.statusSuccess
                                                                        : AppColors.statusWarning,
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                                if (message.requiresClarification == true)
                                                    const Text('⚠️ Klarifikasi Dibutuhkan', style: TextStyle(color: AppColors.statusWarning, fontSize: 11, fontWeight: FontWeight.bold)),
                                            ],
                                        ),
                                        const SizedBox(height: 10),
                                    ],

                                    // Attachments View
                                    if (message.attachments != null && message.attachments!.isNotEmpty) ...[
                                        Wrap(
                                            spacing: 6,
                                            runSpacing: 6,
                                            children: message.attachments!.map((att) {
                                                return Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                                    decoration: BoxDecoration(
                                                        color: AppColors.surfaceDark,
                                                        borderRadius: BorderRadius.circular(6),
                                                        border: Border.all(color: AppColors.glassBorder),
                                                    ),
                                                    child: Text(
                                                        '[${att.type.toUpperCase()}] ${att.content}',
                                                        style: const TextStyle(fontSize: 11, color: AppColors.primaryNeon),
                                                    ),
                                                );
                                            }).toList(),
                                        ),
                                        const SizedBox(height: 10),
                                    ],

                                    // Main Content
                                    SelectableText(
                                        message.content,
                                        style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
                                    ),

                                    // Subagent Delegation Logs
                                    if (message.subagentLogs != null && message.subagentLogs!.isNotEmpty) ...[
                                        const SizedBox(height: 16),
                                        const Divider(color: AppColors.glassBorder),
                                        const SizedBox(height: 8),
                                        const Text('TIM SUB-AGEN NVOIN (DELEGASI):', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textMuted)),
                                        const SizedBox(height: 6),
                                        ...message.subagentLogs!.map((log) {
                                            return Container(
                                                margin: const EdgeInsets.only(top: 6),
                                                padding: const EdgeInsets.all(10),
                                                decoration: BoxDecoration(
                                                    color: AppColors.surfaceDark,
                                                    borderRadius: BorderRadius.circular(8),
                                                ),
                                                child: Column(
                                                    crossAxisAlignment: CrossAxisAlignment.start,
                                                    children: [
                                                        Row(
                                                            children: [
                                                                Icon(
                                                                    log.success ? LucideIcons.checkCircle : LucideIcons.alertCircle,
                                                                    size: 14,
                                                                    color: log.success ? AppColors.statusSuccess : AppColors.statusError,
                                                                ),
                                                                const SizedBox(width: 6),
                                                                Text(
                                                                    log.agentName.toUpperCase(),
                                                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                                                                ),
                                                            ],
                                                        ),
                                                        const SizedBox(height: 4),
                                                        Text(
                                                            log.output,
                                                            style: const TextStyle(fontFamily: 'Courier', fontSize: 11, color: AppColors.textSecondary),
                                                        ),
                                                    ],
                                                ),
                                            );
                                        }).toList(),
                                    ],
                                ],
                            ),
                        ),
                    ),

                    if (isUser) ...[
                        const SizedBox(width: 12),
                        Container(
                            width: 32, height: 32,
                            decoration: BoxDecoration(
                                color: AppColors.surfaceDark,
                                shape: BoxShape.circle,
                                border: Border.all(color: AppColors.glassBorder),
                            ),
                            child: const Icon(LucideIcons.user, size: 16, color: Colors.white),
                        ),
                    ],
                ],
            ),
        );
    }
}
