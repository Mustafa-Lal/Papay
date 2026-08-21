import '../api/api_client.dart';
import '../api/api_endpoints.dart';

class AuthService {
  final ApiClient _apiClient;

  AuthService({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Exchanges an activation key for a session token.
  /// Returns the token string on success.
  Future<String> activate(String activationKey) async {
    final response = await _apiClient.post(
      ApiEndpoints.activate,
      body: {'activation_key': activationKey},
    );
    return response['token'];
  }

  /// Retrieves the current user's role from the backend.
  /// Returns the role string (e.g., 'ADMIN', 'INSURANCE', 'MECHANIC').
  Future<String> getMe() async {
    final response = await _apiClient.get(ApiEndpoints.me);
    return response['role'];
  }

  /// Invalidates the current session on the backend.
  Future<void> logout() async {
    try {
      await _apiClient.post(ApiEndpoints.logout);
    } catch (_) {
      // If logout fails (e.g. token already expired), we don't care, 
      // we'll still clear it locally.
    }
  }
}
