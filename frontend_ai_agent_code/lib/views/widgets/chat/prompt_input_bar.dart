import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../../core/constants/app_colors.dart';
import '../../../controllers/agent_controller.dart';

class PromptInputBar extends StatefulWidget {
    const PromptInputBar({super.key});

    @override
    State<PromptInputBar> createState() => _PromptInputBarState();
}

class _PromptInputBarState extends State<PromptInputBar> {
    final TextEditingController _textController = TextEditingController();

    void _handleSend(AgentController controller) {
        if (_textController.text.trim().isNotEmpty || controller.pendingAttachments.isNotEmpty) {
            controller.sendPrompt(_textController.text);
            _textController.clear();
        }
    }

    void _showMultimodalMenu(BuildContext context, AgentController controller) {
        showModalBottomSheet(
            context: context,
            backgroundColor: AppColors.surfaceCard,
            shape: const RoundedRectangleBorder(
                borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            builder: (ctx) => SafeArea(
                child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                            const Text('ADD MULTIMODAL ATTACHMENT (GEMMA 4 12B)', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                            const SizedBox(height: 14),
                            ListTile(
                                leading: const Icon(LucideIcons.image, color: AppColors.primaryNeon),
                                title: const Text('Images / UI Vision', style: TextStyle(color: Colors.white)),
                                subtitle: const Text('Analyze UI mockup or diagram image', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                                onTap: () {
                                    controller.addAttachment('image', '[Image Attachment: ui_mockup.png]');
                                    Navigator.pop(ctx);
                                },
                            ),
                            ListTile(
                                leading: const Icon(LucideIcons.atSign, color: AppColors.secondaryNeon),
                                title: const Text('Mentions (@files, @subagents)', style: TextStyle(color: Colors.white)),
                                subtitle: const Text('Reference @planner, @coder, or specific file path', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                                onTap: () {
                                    controller.addAttachment('mention', '@coder C:\\Users\\Nvoinvx\\Downloads\\AI_AGENT_CODE\\cli\\main.py');
                                    Navigator.pop(ctx);
                                },
                            ),
                            ListTile(
                                leading: const Icon(LucideIcons.terminal, color: AppColors.accentEmerald),
                                title: const Text('Action / Terminal Execution', style: TextStyle(color: Colors.white)),
                                subtitle: const Text('Trigger shell sandbox on Windows or Arch Linux', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                                onTap: () {
                                    controller.addAttachment('action', 'Run unit tests in sandbox terminal');
                                    Navigator.pop(ctx);
                                },
                            ),
                            ListTile(
                                leading: const Icon(LucideIcons.globe, color: AppColors.accentPurple),
                                title: const Text('Browser / Web Fetch', style: TextStyle(color: Colors.white)),
                                subtitle: const Text('Inspect online documentation or web pages', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                                onTap: () {
                                    controller.addAttachment('browser', 'Fetch documentation from https://docs.flutter.dev');
                                    Navigator.pop(ctx);
                                },
                            ),
                        ],
                    ),
                ),
            ),
        );
    }

    @override
    Widget build(BuildContext context) {
        final controller = context.watch<AgentController>();

        return Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
                color: AppColors.surfaceCard,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.glassBorder),
                boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 20, offset: const Offset(0, 8)),
                ],
            ),
            child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                    // Pending Attachments Chips
                    if (controller.pendingAttachments.isNotEmpty) ...[
                        Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: controller.pendingAttachments.asMap().entries.map((entry) {
                                final idx = entry.key;
                                final att = entry.value;
                                return Chip(
                                    backgroundColor: AppColors.surfaceDark,
                                    side: BorderSide(color: AppColors.primaryNeon.withOpacity(0.4)),
                                    label: Text('${att.type.toUpperCase()}: ${att.content}', style: const TextStyle(fontSize: 11, color: Colors.white)),
                                    deleteIcon: const Icon(Icons.close, size: 14, color: AppColors.textSecondary),
                                    onDeleted: () => controller.removeAttachment(idx),
                                );
                            }).toList(),
                        ),
                        const SizedBox(height: 12),
                    ],

                    // Input Text Row
                    Row(
                        children: [
                            const Icon(LucideIcons.sparkles, color: AppColors.primaryNeon, size: 20),
                            const SizedBox(width: 12),
                            Expanded(
                                child: TextField(
                                    controller: _textController,
                                    style: const TextStyle(color: Colors.white, fontSize: 15),
                                    onSubmitted: (_) => _handleSend(controller),
                                    decoration: const InputDecoration(
                                        hintText: 'Ask Nvoin AI anything (or reference path)...',
                                        hintStyle: TextStyle(color: AppColors.textMuted),
                                        border: InputBorder.none,
                                    ),
                                ),
                            ),
                        ],
                    ),
                    const SizedBox(height: 16),

                    // Bottom Toolbar Row
                    Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                            Row(
                                children: [
                                    // Plus Button (Multimodal Menu: Images, Mentions, Action, Browser)
                                    InkWell(
                                        onTap: () => _showMultimodalMenu(context, controller),
                                        borderRadius: BorderRadius.circular(20),
                                        child: Container(
                                            width: 36, height: 36,
                                            decoration: BoxDecoration(
                                                color: AppColors.surfaceDark,
                                                shape: BoxShape.circle,
                                                border: Border.all(color: AppColors.glassBorder),
                                            ),
                                            child: const Icon(LucideIcons.plus, size: 18, color: AppColors.primaryNeon),
                                        ),
                                    ),
                                    const SizedBox(width: 10),

                                    // Mode Selector Button
                                    _buildDropdownChip(
                                        icon: LucideIcons.layers,
                                        label: controller.selectedMode,
                                        onTap: () {},
                                    ),
                                    const SizedBox(width: 8),

                                    // Deep Think / Auto-Heal Toggle
                                    _buildDropdownChip(
                                        icon: LucideIcons.lightbulb,
                                        label: 'Deep Think',
                                        onTap: () {},
                                    ),
                                ],
                            ),

                            Row(
                                children: [
                                    // Voice Button
                                    Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                        decoration: BoxDecoration(
                                            color: AppColors.surfaceDark,
                                            borderRadius: BorderRadius.circular(20),
                                            border: Border.all(color: AppColors.glassBorder),
                                        ),
                                        child: const Row(
                                            children: [
                                                Icon(LucideIcons.mic, size: 16, color: AppColors.textSecondary),
                                                SizedBox(width: 6),
                                                Text('Voice', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                                            ],
                                        ),
                                    ),
                                    const SizedBox(width: 10),

                                    // Send Button
                                    InkWell(
                                        onTap: () => _handleSend(controller),
                                        borderRadius: BorderRadius.circular(20),
                                        child: Container(
                                            width: 38, height: 38,
                                            decoration: const BoxDecoration(
                                                shape: BoxShape.circle,
                                                gradient: AppColors.heroGradient,
                                            ),
                                            child: const Icon(LucideIcons.send, size: 18, color: Colors.black),
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        );
    }

    Widget _buildDropdownChip({required IconData icon, required String label, required VoidCallback onTap}) {
        return InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(20),
            child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                    color: AppColors.surfaceDark,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.glassBorder),
                ),
                child: Row(
                    children: [
                        Icon(icon, size: 14, color: AppColors.textSecondary),
                        const SizedBox(width: 6),
                        Text(label, style: const TextStyle(fontSize: 12, color: Colors.white)),
                        const SizedBox(width: 4),
                        const Icon(LucideIcons.chevronDown, size: 14, color: AppColors.textSecondary),
                    ],
                ),
            ),
        );
    }
}
