import '../api/api_client.dart';
import '../api/api_endpoints.dart';
import '../api/api_exception.dart';

class AuthService {
  final ApiClient _apiClient;

  AuthService({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Exchanges an activation key for a session token.
  /// Returns a map with 'token' (String) and 'expires_at' (DateTime?).
  Future<Map<String, dynamic>> activate(String activationKey) async {
    final response = await _apiClient.post(
      ApiEndpoints.activate,
      body: {'activation_key': activationKey},
    );
    final expiresAtRaw = response['expires_at'];
    return {
      'token': response['token'] as String,
      'expires_at': expiresAtRaw != null
          ? DateTime.tryParse(expiresAtRaw.toString())
          : null,
    };
  }

  /// Retrieves the current user's role from the backend.
  /// Returns the role string (e.g., 'ADMIN', 'INSURANCE', 'MECHANIC').
  Future<String> getMe() async {
    final response = await _apiClient.get(ApiEndpoints.me);
    return response['role'];
  }

  /// Checks if the current app version is allowed by the backend.
  ///
  /// Returns true  → version matches, allow access.
  /// Returns false → version mismatch OR any error → show update screen.
  ///
  /// Fail-closed: if the version check cannot be confirmed (404, network
  /// error, server error), access is denied. Admin users are exempted
  /// from this check in auth_state.dart before this is called.
  Future<bool> checkVersion(String currentVersion) async {
    if (currentVersion.isEmpty) return false;

    try {
      // Pass version as a proper query parameter map — NOT via string
      // interpolation, which causes ?version=1.0.1 to be URL-encoded
      // into the path (%3Fversion%3D1.0.1) → 404.
      final response = await _apiClient.get(
        ApiEndpoints.versionCheck,
        queryParameters: {'version': currentVersion},
      );
      return response['match'] == true;
    } catch (_) {
      // Fail-closed: any error (404, network down, server error) is treated
      // as a version mismatch and the update screen is shown.
      return false;
    }
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
