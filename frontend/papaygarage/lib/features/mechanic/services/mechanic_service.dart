import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/mechanic_models.dart';

class MechanicService {
  final ApiClient _apiClient;

  MechanicService({required ApiClient apiClient}) : _apiClient = apiClient;

  // -------------------------------------------------------
  // INVOICES
  // -------------------------------------------------------

  Future<List<MechanicInvoiceSummary>> getInvoices({
    String? plateNumber,
    String? startDate,
    String? endDate,
    int limit = 20,
    int offset = 0,
  }) async {
    final params = <String, String>{
      'limit': limit.toString(),
      'offset': offset.toString(),
    };
    if (plateNumber != null && plateNumber.isNotEmpty) {
      params['plate_number'] = plateNumber;
    }
    if (startDate != null) params['start_date'] = startDate;
    if (endDate != null) params['end_date'] = endDate;

    final response = await _apiClient.get(
      ApiEndpoints.mechanicInvoices,
      queryParameters: params,
    );

    final list = (response['customers'] as List);
    return list.map((e) => MechanicInvoiceSummary.fromJson(e)).toList();
  }

  Future<MechanicInvoice> getInvoice(int invoiceId) async {
    final response = await _apiClient.get('${ApiEndpoints.mechanicInvoices}/$invoiceId');
    return MechanicInvoice.fromJson(response);
  }

  Future<MechanicInvoice> createInvoice({
    required String plateNumber,
    required double laborCharges,
    required String paymentStatus,
    required String? customerName,
    required String? phoneNumber,
    required String? qid,
    required List<Map<String, dynamic>> items,
  }) async {
    final body = {
      'plate_number': plateNumber,
      'labor_charges': laborCharges,
      'payment_status': paymentStatus,
      'customer': {
        'customer_name': customerName,
        'phone_number': phoneNumber,
        'qid': qid,
      },
      'items': items,
    };
    final response = await _apiClient.post(ApiEndpoints.mechanicInvoices, body: body);
    return MechanicInvoice.fromJson(response);
  }

  Future<MechanicInvoice> updateInvoice(int invoiceId, Map<String, dynamic> fields) async {
    final response = await _apiClient.put(
      '${ApiEndpoints.mechanicInvoices}/$invoiceId',
      body: fields,
    );
    return MechanicInvoice.fromJson(response);
  }

  Future<void> deleteInvoice(int invoiceId) async {
    await _apiClient.delete('${ApiEndpoints.mechanicInvoices}/$invoiceId');
  }

  // -------------------------------------------------------
  // CUSTOMER
  // -------------------------------------------------------

  Future<void> updateCustomer(int customerId, Map<String, dynamic> fields) async {
    await _apiClient.put('${ApiEndpoints.mechanicCustomers}/$customerId', body: fields);
  }

  // -------------------------------------------------------
  // ITEMS
  // -------------------------------------------------------

  Future<MechanicItem> createItem(int invoiceId, Map<String, dynamic> fields) async {
    final response = await _apiClient.post('${ApiEndpoints.mechanicInvoices}/$invoiceId/items', body: fields);
    return MechanicItem.fromJson(response);
  }

  Future<void> updateItem(int itemId, Map<String, dynamic> fields) async {
    await _apiClient.put('${ApiEndpoints.mechanicItems}/$itemId', body: fields);
  }

  Future<void> deleteItem(int itemId) async {
    await _apiClient.delete('${ApiEndpoints.mechanicItems}/$itemId');
  }
}
