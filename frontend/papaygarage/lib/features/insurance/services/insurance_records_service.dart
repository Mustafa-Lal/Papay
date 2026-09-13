import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class InsuranceRecordsService {
  final ApiClient _apiClient;

  InsuranceRecordsService({required ApiClient apiClient}) : _apiClient = apiClient;

  // ---------------------------------------------------------------------------
  // Incomes
  // ---------------------------------------------------------------------------

  Future<void> createIncome(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.insuranceIncomes, body: data);
  }

  Future<List<dynamic>> getIncomes({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.insuranceIncomes,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['incomes'] ?? [];
  }

  Future<void> deleteIncome(int id) async {
    await _apiClient.delete('${ApiEndpoints.insuranceIncomes}/$id');
  }

  Future<void> updateIncome(int id, Map<String, dynamic> data) async {
    await _apiClient.put('${ApiEndpoints.insuranceIncomes}/$id', body: data);
  }

  // ---------------------------------------------------------------------------
  // Expenses
  // ---------------------------------------------------------------------------

  Future<void> createExpense(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.insuranceExpenses, body: data);
  }

  Future<List<dynamic>> getExpenses({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.insuranceExpenses,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['expenses'] ?? [];
  }

  Future<void> deleteExpense(int id) async {
    await _apiClient.delete('${ApiEndpoints.insuranceExpenses}/$id');
  }

  Future<void> updateExpense(int id, Map<String, dynamic> data) async {
    await _apiClient.put('${ApiEndpoints.insuranceExpenses}/$id', body: data);
  }
}
