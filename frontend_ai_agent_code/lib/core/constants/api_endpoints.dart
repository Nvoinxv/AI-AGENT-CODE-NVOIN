class ApiEndpoints {
    ApiEndpoints._();

    static const String baseUrl = 'http://localhost:8000/api/v1';
    
    static const String status = '$baseUrl/status';
    static const String chat = '$baseUrl/chat';
    static const String workspaceFiles = '$baseUrl/workspace/files';
}
