import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../../core/constants/app_colors.dart';

class QuickActionCard extends StatelessWidget {
    final IconData icon;
    final String title;
    final String subtitle;
    final VoidCallback onTap;

    const QuickActionCard({
        super.key,
        required this.icon,
        required this.title,
        required this.subtitle,
        required this.onTap,
    });

    @override
    Widget build(BuildContext context) {
        return Expanded(
            child: InkWell(
                onTap: onTap,
                borderRadius: BorderRadius.circular(16),
                child: Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                        color: AppColors.surfaceCard,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.glassBorder),
                        boxShadow: [
                            BoxShadow(
                                color: Colors.black.withOpacity(0.2),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                            ),
                        ],
                    ),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                            Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                    Icon(icon, size: 22, color: AppColors.primaryNeon),
                                    const Icon(LucideIcons.arrowUpRight, size: 18, color: AppColors.textSecondary),
                                ],
                            ),
                            const SizedBox(height: 16),
                            Text(
                                title,
                                style: const TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.white,
                                ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                                subtitle,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    fontSize: 12,
                                    color: AppColors.textSecondary,
                                    height: 1.4,
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        );
    }
}
