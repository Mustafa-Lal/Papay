import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class RecordsService {
  final ApiClient _apiClient;

  RecordsService({required ApiClient apiClient}) : _apiClient = apiClient;

  // Products
  Future<void> createProduct(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.products, body: data);
  }

  Future<List<dynamic>> getProducts({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.products,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['products'] ?? [];
  }

  Future<void> deleteProduct(int id) async {
    await _apiClient.delete('${ApiEndpoints.products}/$id');
  }

  // Rent
  Future<void> createRent(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.rent, body: data);
  }

  Future<List<dynamic>> getRents({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.rent,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    // rent endpoint may return list directly or wrapped
    if (response is List) return response;
    return (response as Map<String, dynamic>)['rents'] ?? response['items'] ?? [];
  }

  Future<void> deleteRent(int id) async {
    await _apiClient.delete('${ApiEndpoints.rent}/$id');
  }

  // Salary
  Future<void> createSalary(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.salaries, body: data);
  }

  Future<List<dynamic>> getSalaries(int year, int month, {int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      '${ApiEndpoints.salaries}/$year/$month',
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['salaries'] ?? [];
  }

  Future<void> deleteSalary(int id) async {
    await _apiClient.delete('${ApiEndpoints.salaries}/$id');
  }

  // Utility Bills
  Future<void> createUtilityBill(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.utilityBills, body: data);
  }

  Future<List<dynamic>> getUtilityBills(int year, int month, {int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      '${ApiEndpoints.utilityBills}/$year/$month',
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['bills'] ?? [];
  }

  Future<void> deleteUtilityBill(int id) async {
    await _apiClient.delete('${ApiEndpoints.utilityBills}/$id');
  }

  // Profits
  Future<void> createProfit(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.profits, body: data);
  }

  Future<List<dynamic>> getProfits({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.profits,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['profits'] ?? [];
  }

  Future<void> deleteProfit(int id) async {
    await _apiClient.delete('${ApiEndpoints.profits}/$id');
  }

  // Expenses
  Future<void> createExpense(Map<String, dynamic> data) async {
    await _apiClient.post(ApiEndpoints.expenses, body: data);
  }

  Future<List<dynamic>> getExpenses({int limit = 10, int offset = 0}) async {
    final response = await _apiClient.get(
      ApiEndpoints.expenses,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return response['expenses'] ?? [];
  }

  Future<void> deleteExpense(int id) async {
    await _apiClient.delete('${ApiEndpoints.expenses}/$id');
  }
}
