import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';

class HeroWelcome extends StatelessWidget {
    const HeroWelcome({super.key});

    @override
    Widget build(BuildContext context) {
        return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
                // Glowing Energy Sphere / Orb Logo
                Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const RadialGradient(
                            colors: [AppColors.primaryNeon, AppColors.secondaryNeon, Color(0xFF0D1D30)],
                            center: Alignment(-0.3, -0.3),
                            radius: 1.0,
                        ),
                        boxShadow: [
                            BoxShadow(
                                color: AppColors.primaryNeon.withOpacity(0.5),
                                blurRadius: 40,
                                spreadRadius: 2,
                            ),
                            BoxShadow(
                                color: AppColors.accentEmerald.withOpacity(0.3),
                                blurRadius: 20,
                                spreadRadius: -5,
                            ),
                        ],
                    ),
                    child: Center(
                        child: Container(
                            width: 36,
                            height: 36,
                            decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.white.withOpacity(0.25),
                            ),
                        ),
                    ),
                ),
                const SizedBox(height: 24),
                
                const Text(
                    'WELCOME BACK TO NVOIN AI',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 3.0,
                        color: AppColors.textSecondary,
                    ),
                ),
                const SizedBox(height: 8),

                const Text(
                    'Bring your code & ideas to life today',
                    style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                    ),
                ),
            ],
        );
    }
}
