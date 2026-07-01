import 'package:flutter/material.dart';

class AppColors {
    AppColors._();

    // Background & Surface
    static const Color background = Color(0xFF0B0E14);
    static const Color surfaceDark = Color(0xFF121620);
    static const Color surfaceCard = Color(0xFF191F2D);
    static const Color glassBorder = Color(0xFF283145);

    // Neon & Glow Accents (Inspired by glowing center sphere & dark cyan gradients)
    static const Color primaryNeon = Color(0xFF00F2FE);
    static const Color secondaryNeon = Color(0xFF4FACFE);
    static const Color accentEmerald = Color(0xFF00E6A7);
    static const Color accentPurple = Color(0xFF9F55FF);

    // Text Colors
    static const Color textPrimary = Color(0xFFFFFFFF);
    static const Color textSecondary = Color(0xFF90A0B7);
    static const Color textMuted = Color(0xFF5A6982);

    // Status Colors
    static const Color statusSuccess = Color(0xFF10B981);
    static const Color statusWarning = Color(0xFFF59E0B);
    static const Color statusError = Color(0xFFEF4444);

    // Gradients
    static const LinearGradient heroGradient = LinearGradient(
        colors: [primaryNeon, secondaryNeon],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
    );

    static const LinearGradient cardGradient = LinearGradient(
        colors: [Color(0xFF1E2638), Color(0xFF141925)],
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
    );
}
