import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/insurance_models.dart';

class InsuranceService {
  final ApiClient _apiClient;

  InsuranceService({required ApiClient apiClient}) : _apiClient = apiClient;

  // -------------------------------------------------------
  // INVOICES
  // -------------------------------------------------------

  Future<List<InsuranceInvoiceSummary>> getInvoices({
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
      ApiEndpoints.insuranceInvoices,
      queryParameters: params,
    );

    final list = (response['customers'] as List);
    return list.map((e) => InsuranceInvoiceSummary.fromJson(e)).toList();
  }

  Future<InsuranceInvoice> getInvoice(int invoiceId) async {
    final response = await _apiClient.get('${ApiEndpoints.insuranceInvoices}/$invoiceId');
    return InsuranceInvoice.fromJson(response);
  }

  Future<InsuranceInvoice> createInvoice({
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
    final response = await _apiClient.post(ApiEndpoints.insuranceInvoices, body: body);
    return InsuranceInvoice.fromJson(response);
  }

  Future<InsuranceInvoice> updateInvoice(int invoiceId, Map<String, dynamic> fields) async {
    final response = await _apiClient.put(
      '${ApiEndpoints.insuranceInvoices}/$invoiceId',
      body: fields,
    );
    return InsuranceInvoice.fromJson(response);
  }

  Future<void> deleteInvoice(int invoiceId) async {
    await _apiClient.delete('${ApiEndpoints.insuranceInvoices}/$invoiceId');
  }

  // -------------------------------------------------------
  // CUSTOMER
  // -------------------------------------------------------

  Future<void> updateCustomer(int customerId, Map<String, dynamic> fields) async {
    await _apiClient.put('${ApiEndpoints.insuranceCustomers}/$customerId', body: fields);
  }

  // -------------------------------------------------------
  // ITEMS
  // -------------------------------------------------------

  Future<InsuranceItem> createItem(int invoiceId, Map<String, dynamic> fields) async {
    final response = await _apiClient.post('${ApiEndpoints.insuranceInvoices}/$invoiceId/items', body: fields);
    return InsuranceItem.fromJson(response);
  }

  Future<void> updateItem(int itemId, Map<String, dynamic> fields) async {
    await _apiClient.put('${ApiEndpoints.insuranceItems}/$itemId', body: fields);
  }

  Future<void> deleteItem(int itemId) async {
    await _apiClient.delete('${ApiEndpoints.insuranceItems}/$itemId');
  }

  // -------------------------------------------------------
  // IMAGES
  // -------------------------------------------------------

  Future<InsuranceImage> uploadImage({
    required int invoiceId,
    required String imageType,
    required String filename,
    required List<int> bytes,
  }) async {
    final response = await _apiClient.postMultipart(
      '${ApiEndpoints.insuranceInvoices}/$invoiceId/images',
      fileField: 'file',
      filename: filename,
      bytes: bytes,
      fields: {
        'image_type': imageType,
      },
    );
    return InsuranceImage.fromJson(response);
  }

  Future<void> deleteImage(int imageId) async {
    await _apiClient.delete('${ApiEndpoints.insuranceImages}/$imageId');
  }
}
