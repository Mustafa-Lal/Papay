import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/access_key_model.dart';

class AdminService {
  final ApiClient _apiClient;

  AdminService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<List<AccessKeyModel>> getAccessKeys() async {
    final response = await _apiClient.get(ApiEndpoints.adminAccessKeys);
    // response is typically a list of JSON objects
    if (response is List) {
      return response.map((json) => AccessKeyModel.fromJson(json)).toList();
    }
    return [];
  }

  Future<AccessKeyCreateResponse> createAccessKey(int roleId) async {
    final response = await _apiClient.post(
      ApiEndpoints.adminAccessKeys,
      body: {'role_id': roleId},
    );
    return AccessKeyCreateResponse.fromJson(response);
  }

  Future<void> activateKey(int keyId) async {
    await _apiClient.patch('${ApiEndpoints.adminAccessKeys}/$keyId/activate');
  }

  Future<void> deactivateKey(int keyId) async {
    await _apiClient.patch('${ApiEndpoints.adminAccessKeys}/$keyId/deactivate');
  }

  Future<void> deleteKey(int keyId) async {
    await _apiClient.delete('${ApiEndpoints.adminAccessKeys}/$keyId');
  }
}
