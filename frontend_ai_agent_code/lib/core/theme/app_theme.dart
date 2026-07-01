import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/app_colors.dart';

class AppTheme {
    AppTheme._();

    static ThemeData get darkTheme {
        return ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
            scaffoldBackgroundColor: AppColors.background,
            primaryColor: AppColors.primaryNeon,
            textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).copyWith(
                headlineLarge: GoogleFonts.outfit(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.5,
                ),
                titleLarge: GoogleFonts.outfit(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                ),
            ),
            colorScheme: const ColorScheme.dark(
                primary: AppColors.primaryNeon,
                secondary: AppColors.secondaryNeon,
                surface: AppColors.surfaceDark,
                background: AppColors.background,
            ),
        );
    }
}
