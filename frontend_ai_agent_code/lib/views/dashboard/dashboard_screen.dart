import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../controllers/agent_controller.dart';
import '../widgets/sidebar/app_sidebar.dart';
import '../widgets/dashboard/hero_welcome.dart';
import '../widgets/dashboard/quick_action_card.dart';
import '../widgets/chat/prompt_input_bar.dart';
import '../widgets/chat/message_bubble.dart';
import '../widgets/common/project_selector_dialog.dart';

class DashboardScreen extends StatelessWidget {
    const DashboardScreen({super.key});

    @override
    Widget build(BuildContext context) {
        final controller = context.watch<AgentController>();

        return Scaffold(
            body: Row(
                children: [
                    // Left Sidebar
                    const AppSidebar(),

                    // Main Content Area
                    Expanded(
                        child: Stack(
                            children: [
                                // Background subtle glowing gradient effect
                                Positioned(
                                    top: -100, right: -100,
                                    child: Container(
                                        width: 500, height: 500,
                                        decoration: BoxDecoration(
                                            shape: BoxShape.circle,
                                            color: AppColors.primaryNeon.withOpacity(0.04),
                                        ),
                                    ),
                                ),

                                // Content Column
                                Column(
                                    children: [
                                        // Top Bar
                                        _buildTopBar(context, controller),

                                        // Main Body (Hero or Messages)
                                        Expanded(
                                            child: controller.messages.isEmpty
                                                ? _buildEmptyDashboard(controller)
                                                : _buildChatList(controller),
                                        ),

                                        // Bottom Prompt Input Bar
                                        const Padding(
                                            padding: EdgeInsets.symmetric(horizontal: 40, vertical: 20),
                                            child: PromptInputBar(),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        );
    }

    Widget _buildTopBar(BuildContext context, AgentController controller) {
        return Container(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                    Row(
                        children: [
                            // Tombol Proyek Workspace ala AntiGravity
                            InkWell(
                                onTap: () => showDialog(
                                    context: context,
                                    builder: (_) => const ProjectSelectorDialog(),
                                ),
                                borderRadius: BorderRadius.circular(20),
                                child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                                    decoration: BoxDecoration(
                                        color: AppColors.primaryNeon.withOpacity(0.15),
                                        borderRadius: BorderRadius.circular(20),
                                        border: Border.all(color: AppColors.primaryNeon),
                                    ),
                                    child: Row(
                                        children: [
                                            const Icon(LucideIcons.folderKanban, size: 14, color: AppColors.primaryNeon),
                                            const SizedBox(width: 8),
                                            Text(
                                                controller.currentProject?.name ?? 'Pilih Proyek...',
                                                style: const TextStyle(fontSize: 12, color: AppColors.primaryNeon, fontWeight: FontWeight.bold),
                                            ),
                                            const SizedBox(width: 4),
                                            const Icon(LucideIcons.chevronDown, size: 14, color: AppColors.primaryNeon),
                                        ],
                                    ),
                                ),
                            ),
                            const SizedBox(width: 12),

                            // Mode Pill
                            Container(
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                                decoration: BoxDecoration(
                                    color: AppColors.surfaceCard,
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: AppColors.glassBorder),
                                ),
                                child: Row(
                                    children: [
                                        const Icon(LucideIcons.sliders, size: 14, color: AppColors.primaryNeon),
                                        const SizedBox(width: 8),
                                        Text(controller.selectedMode, style: const TextStyle(fontSize: 12, color: Colors.white, fontWeight: FontWeight.w500)),
                                    ],
                                ),
                            ),
                        ],
                    ),

                    // Right Links & Avatar
                    Row(
                        children: [
                            const Text('Dashboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(width: 24),
                            const Text('Settings', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                            const SizedBox(width: 24),
                            const Text('Help & Support', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                            const SizedBox(width: 24),
                            Container(
                                width: 32, height: 32,
                                decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(color: AppColors.primaryNeon),
                                    color: AppColors.surfaceCard,
                                ),
                                child: const Center(child: Text('NV', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white))),
                            ),
                        ],
                    ),
                ],
            ),
        );
    }

    Widget _buildEmptyDashboard(AgentController controller) {
        return Center(
            child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                        const HeroWelcome(),
                        const SizedBox(height: 48),

                        // Quick Action Cards Row
                        Row(
                            children: [
                                QuickActionCard(
                                    icon: LucideIcons.code2,
                                    title: 'Autonomous Codex Dev',
                                    subtitle: 'Refactor, write tests, or generate clean codebase structures.',
                                    onTap: () => controller.sendPrompt('Tolong analisis workspace ini dan refactor modul utama.'),
                                ),
                                const SizedBox(width: 16),
                                QuickActionCard(
                                    icon: LucideIcons.terminal,
                                    title: 'Terminal Sandbox CLI',
                                    subtitle: 'Run shell commands securely across Windows & Arch Linux.',
                                    onTap: () => controller.sendPrompt('Jalankan unit test pytest di terminal sandbox kita.'),
                                ),
                                const SizedBox(width: 16),
                                QuickActionCard(
                                    icon: LucideIcons.image,
                                    title: 'Multimodal Vision & Web',
                                    subtitle: 'Analyze UI images, diagrams, or fetch web docs.',
                                    onTap: () => controller.sendPrompt('Periksa desain UI mockup dan cocokkan dengan kode front-end.'),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        );
    }

    Widget _buildChatList(AgentController controller) {
        return ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 20),
            itemCount: controller.messages.length + (controller.isLoading ? 1 : 0),
            itemBuilder: (ctx, idx) {
                if (idx == controller.messages.length) {
                    return _buildLoadingIndicator();
                }
                return MessageBubble(message: controller.messages[idx]);
            },
        );
    }

    Widget _buildLoadingIndicator() {
        return Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Row(
                children: [
                    Container(
                        width: 28, height: 28,
                        decoration: const BoxDecoration(shape: BoxShape.circle, color: AppColors.surfaceCard),
                        child: const Center(
                            child: SizedBox(
                                width: 14, height: 14,
                                child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primaryNeon),
                            ),
                        ),
                    ),
                    const SizedBox(width: 12),
                    const Text('Nvoin AI Orchestrator is analyzing & delegating to subagents...', style: TextStyle(color: AppColors.textSecondary, fontSize: 13, fontStyle: FontStyle.italic)),
                ],
            ),
        );
    }
}
