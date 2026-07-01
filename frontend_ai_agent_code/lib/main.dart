import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'controllers/agent_controller.dart';
import 'views/dashboard/dashboard_screen.dart';
import 'views/screens/auth/login_screen.dart';

void main() {
    WidgetsFlutterBinding.ensureInitialized();
    runApp(const NvoinAiApp());
}

class NvoinAiApp extends StatelessWidget {
    const NvoinAiApp({super.key});

    @override
    Widget build(BuildContext context) {
        return MultiProvider(
            providers: [
                ChangeNotifierProvider(create: (_) => AgentController()),
            ],
            child: MaterialApp(
                title: 'Nvoin AI Agent Code',
                debugShowCheckedModeBanner: false,
                theme: AppTheme.darkTheme,
                home: Consumer<AgentController>(
                    builder: (ctx, ctrl, _) {
                        return ctrl.isLoggedIn ? const DashboardScreen() : const LoginScreen();
                    },
                ),
            ),
        );
    }
}
