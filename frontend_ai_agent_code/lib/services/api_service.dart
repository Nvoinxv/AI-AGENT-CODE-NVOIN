import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_endpoints.dart';
import '../models/chat_message.dart';
import '../models/system_status.dart';

class ApiService {
    Future<SystemStatus?> checkStatus() async {
        try {
            final response = await http.get(Uri.parse(ApiEndpoints.status));
            if (response.statusCode == 200) {
                return SystemStatus.fromJson(json.decode(response.body));
            }
        } catch (e) {
            // Server belum aktif / fallback ke simulasi offline
        }
        return null;
    }

    Future<Map<String, dynamic>> sendChatMessage({
        required String prompt,
        String? sessionId,
        List<MultimodalAttachment>? attachments,
        String mode = 'fugu_auto',
    }) async {
        try {
            final payload = {
                'prompt': prompt,
                if (sessionId != null) 'session_id': sessionId,
                if (attachments != null)
                    'attachments': attachments.map((a) => a.toJson()).toList(),
                'mode': mode,
            };

            final response = await http.post(
                Uri.parse(ApiEndpoints.chat),
                headers: {'Content-Type': 'application/json'},
                body: json.encode(payload),
            );

            if (response.statusCode == 200) {
                return json.decode(response.body);
            }
        } catch (e) {
            // Simulasi lokal jika backend Python FastAPI belum dijalankan
        }

        // Fallback simulasi respons cerdas Nvoin AI
        return {
            'session_id': sessionId ?? 'demo_session',
            'response': '=== [Simulasi Nvoin AI Agent Code - Gemma 4 12B] ===\n'
                'Instruksi Anda: "$prompt"\n\n'
                'Manajer Nvoin telah mengevaluasi permintaan ini. '
                'Jika server FastAPI (`python -m api.server`) aktif, delegasi agen (Planner/Coder/Executor/Reviewer) '
                'dan eksekusi terminal akan dijalankan secara langsung di workspace Anda!',
            'subagent_logs': [],
            'os_info': {'os_name': 'Windows / Arch Linux (Simulated)'}
        };
    }
}
