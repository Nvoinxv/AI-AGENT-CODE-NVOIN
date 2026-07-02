import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:provider/provider.dart';
import '../../../core/constants/app_colors.dart';
import '../../../controllers/agent_controller.dart';

class AppSidebar extends StatelessWidget {
    const AppSidebar({super.key});

    @override
    Widget build(BuildContext context) {
        final controller = context.watch<AgentController>();

        return Container(
            width: 260,
            decoration: const BoxDecoration(
                color: AppColors.surfaceDark,
                border: Border(right: BorderSide(color: AppColors.glassBorder)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
            child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                    // Brand Header
                    Row(
                        children: [
                            Container(
                                width: 32,
                                height: 32,
                                decoration: const BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: AppColors.heroGradient,
                                    boxShadow: [
                                        BoxShadow(color: AppColors.primaryNeon, blurRadius: 10, spreadRadius: -2)
                                    ],
                                ),
                                child: const Icon(LucideIcons.cpu, size: 18, color: Colors.black),
                            ),
                            const SizedBox(width: 12),
                            const Text(
                                'Nvoin AI',
                                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                            ),
                        ],
                    ),
                    const SizedBox(height: 24),

                    // New Chat Button
                    InkWell(
                        onTap: controller.startNewChat,
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                            decoration: BoxDecoration(
                                gradient: LinearGradient(
                                    colors: [AppColors.primaryNeon.withOpacity(0.15), AppColors.surfaceCard],
                                ),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: AppColors.primaryNeon.withOpacity(0.4)),
                            ),
                            child: const Row(
                                children: [
                                    Icon(LucideIcons.plusCircle, size: 18, color: AppColors.primaryNeon),
                                    SizedBox(width: 10),
                                    Text('New Chat', style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
                                ],
                            ),
                        ),
                    ),
                    const SizedBox(height: 28),

                    // FEATURES SECTION
                    const Text('FEATURES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textMuted, letterSpacing: 1.2)),
                    const SizedBox(height: 12),
                    _buildNavItem(LucideIcons.code2, 'Codex Auto-Dev', true),
                    _buildNavItem(LucideIcons.image, 'Vision & Images', false),
                    _buildNavItem(LucideIcons.terminal, 'Terminal Sandbox', false),
                    _buildNavItem(LucideIcons.layers, 'Projects & Files', false),
                    _buildNavItem(LucideIcons.settings, 'QLoRA Trainer', false),
                    
                    const SizedBox(height: 28),

                    // YOUR CHATS SECTION
                    const Text('YOUR CHATS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textMuted, letterSpacing: 1.2)),
                    const SizedBox(height: 12),
                    Expanded(
                        child: ListView(
                            children: [
                                _buildChatHistoryItem('Refactor Auth Module'),
                                _buildChatHistoryItem('Analyze UI Mockup Image'),
                                _buildChatHistoryItem('Run Pytest on Windows'),
                                _buildChatHistoryItem('Generate Flutter UI Components'),
                            ],
                        ),
                    ),

                    // Bottom System Status Card
                    Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                            gradient: AppColors.cardGradient,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: AppColors.glassBorder),
                        ),
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                                Row(
                                    children: [
                                        Container(
                                            width: 8, height: 8,
                                            decoration: const BoxDecoration(color: AppColors.statusSuccess, shape: BoxShape.circle),
                                        ),
                                        const SizedBox(width: 8),
                                        const Text('Gemini 3.5 & Gemma 31B Active', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white)),
                                    ],
                                ),
                                const SizedBox(height: 6),
                                const Text('Cloud AI Agent Ready', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                            ],
                        ),
                    ),
                ],
            ),
        );
    }

    Widget _buildNavItem(IconData icon, String label, bool isActive) {
        return Container(
            margin: const EdgeInsets.only(bottom: 4),
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
            decoration: BoxDecoration(
                color: isActive ? AppColors.surfaceCard : Colors.transparent,
                borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
                children: [
                    Icon(icon, size: 18, color: isActive ? AppColors.primaryNeon : AppColors.textSecondary),
                    const SizedBox(width: 12),
                    Text(label, style: TextStyle(color: isActive ? Colors.white : AppColors.textSecondary, fontSize: 13, fontWeight: isActive ? FontWeight.w600 : FontWeight.normal)),
                ],
            ),
        );
    }

    Widget _buildChatHistoryItem(String title) {
        return Padding(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
            child: Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
            ),
        );
    }
}
