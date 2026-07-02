class SystemStatus {
    final String status;
    final String agent;
    final String llmBackend;
    final String modelName;
    final Map<String, dynamic> osInfo;

    SystemStatus({
        required this.status,
        required this.agent,
        required this.llmBackend,
        required this.modelName,
        required this.osInfo,
    });

    factory SystemStatus.fromJson(Map<String, dynamic> json) {
        return SystemStatus(
            status: json['status'] ?? 'offline',
            agent: json['agent'] ?? 'Nvoin AI',
            llmBackend: json['llm_backend'] ?? 'gemini',
            modelName: json['model_name'] ?? 'gemini-3.5-flash',
            osInfo: json['os_info'] ?? {},
        );
    }
}
