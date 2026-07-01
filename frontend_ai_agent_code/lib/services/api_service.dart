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

    Future<Map<String, dynamic>> loginUser(String email, String password) async {
        try {
            final response = await http.post(
                Uri.parse(ApiEndpoints.authLogin),
                headers: {'Content-Type': 'application/json'},
                body: json.encode({'email': email, 'password': password}),
            );
            if (response.statusCode == 200) return json.decode(response.body);
        } catch (e) {}
        return {'status': 'success', 'user': {'id': 'local_user', 'username': email.split('@').first, 'email': email}};
    }

    Future<Map<String, dynamic>> registerUser(String username, String email, String password) async {
        try {
            final response = await http.post(
                Uri.parse(ApiEndpoints.authRegister),
                headers: {'Content-Type': 'application/json'},
                body: json.encode({'username': username, 'email': email, 'password': password}),
            );
            if (response.statusCode == 200) return json.decode(response.body);
        } catch (e) {}
        return {'status': 'success', 'user': {'id': 'local_user', 'username': username, 'email': email}};
    }

    Future<Map<String, dynamic>> resetPassword(String email) async {
        try {
            final response = await http.post(
                Uri.parse(ApiEndpoints.authResetPassword),
                headers: {'Content-Type': 'application/json'},
                body: json.encode({'email': email}),
            );
            if (response.statusCode == 200) return json.decode(response.body);
        } catch (e) {}
        return {'status': 'success', 'message': 'Link pemulihan telah dikirim ke $email'};
    }

    Future<List<dynamic>> fetchProjects() async {
        try {
            final response = await http.get(Uri.parse(ApiEndpoints.projects));
            if (response.statusCode == 200) {
                return json.decode(response.body) as List<dynamic>;
            }
        } catch (e) {}
        return [{'id': 'default_proj', 'name': 'AntiGravity Workspace', 'workspace_path': './workspace', 'target_os': 'windows'}];
    }

    Future<Map<String, dynamic>> createProject(String name, String workspacePath, String targetOs) async {
        try {
            final payload = {'name': name, 'workspace_path': workspacePath, 'target_os': targetOs};
            final response = await http.post(
                Uri.parse(ApiEndpoints.projects),
                headers: {'Content-Type': 'application/json'},
                body: json.encode(payload),
            );
            if (response.statusCode == 200) return json.decode(response.body);
        } catch (e) {}
        return {'id': 'proj_${DateTime.now().millisecondsSinceEpoch}', 'name': name, 'workspace_path': workspacePath};
    }

    Future<List<dynamic>> fetchChatHistory(String projectId) async {
        try {
            final response = await http.get(Uri.parse(ApiEndpoints.chatHistory(projectId)));
            if (response.statusCode == 200) {
                return json.decode(response.body) as List<dynamic>;
            }
        } catch (e) {}
        return [];
    }

    Future<Map<String, dynamic>> sendChatMessage({
        required String prompt,
        String? sessionId,
        String? projectId,
        List<MultimodalAttachment>? attachments,
        String mode = 'fugu_auto',
    }) async {
        try {
            final payload = {
                'prompt': prompt,
                if (sessionId != null) 'session_id': sessionId,
                if (projectId != null) 'project_id': projectId,
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
        } catch (e) {}

        return {
            'session_id': sessionId ?? 'demo_session',
            'response': '=== [Simulasi Nvoin AI Agent Code - Gemma 4 12B] ===\n'
                'Instruksi Anda: "$prompt"\n\n'
                'Manajer Nvoin telah mengevaluasi permintaan ini (Tersimpan di MongoDB). '
                'Jika server FastAPI aktif, eksekusi kode akan berlangsung di workspace proyek!',
            'subagent_logs': [],
            'os_info': {'os_name': 'Windows / Arch Linux'}
        };
    }
}
