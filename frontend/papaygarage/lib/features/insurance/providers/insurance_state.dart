import 'package:flutter/material.dart';
import '../models/insurance_models.dart';
import '../services/insurance_service.dart';
import '../../../core/api/api_exception.dart';

class InsuranceState extends ChangeNotifier {
  final InsuranceService _service;

  List<InsuranceInvoiceSummary> _invoices = [];
  bool _isLoading = false;
  String? _errorMessage;
  int _total = 0;
  int _offset = 0;
  static const int _limit = 20;

  // Filters
  String? _plateFilter;
  String? _startDateFilter;
  String? _endDateFilter;

  List<InsuranceInvoiceSummary> get invoices => _invoices;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int get total => _total;
  bool get hasMore => _invoices.length < _total;

  InsuranceState({required InsuranceService service}) : _service = service;

  int _currentPage = 1;
  int get currentPage => _currentPage;
  bool _hasMore = true;
  bool get canGoNext => _hasMore;
  bool get canGoPrev => _currentPage > 1;

  void setFilters({String? plate, String? startDate, String? endDate}) {
    _plateFilter = plate?.isEmpty == true ? null : plate;
    _startDateFilter = startDate;
    _endDateFilter = endDate;
    _currentPage = 1;
    _offset = 0;
    _invoices = [];
    _hasMore = true;
    fetchInvoices();
  }

  Future<void> fetchInvoices() async {
    _setLoading(true);
    try {
      final result = await _service.getInvoices(
        plateNumber: _plateFilter,
        startDate: _startDateFilter,
        endDate: _endDateFilter,
        limit: _limit,
        offset: _offset,
      );
      _hasMore = result.length == _limit;
      _invoices = result;
    } on ApiException catch (e) {
      _errorMessage = e.message;
    } catch (e) {
      _errorMessage = 'Failed to load invoices.';
    } finally {
      _setLoading(false);
    }
  }

  void nextPage() {
    if (canGoNext) {
      _currentPage++;
      _offset = (_currentPage - 1) * _limit;
      fetchInvoices();
    }
  }

  void previousPage() {
    if (canGoPrev) {
      _currentPage--;
      _offset = (_currentPage - 1) * _limit;
      fetchInvoices();
    }
  }

  Future<InsuranceInvoice?> getInvoiceDetail(int invoiceId) async {
    try {
      return await _service.getInvoice(invoiceId);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
      return null;
    } catch (_) {
      _errorMessage = 'Failed to load invoice details.';
      notifyListeners();
      return null;
    }
  }

  Future<InsuranceInvoice?> createInvoice({
    required String plateNumber,
    required double laborCharges,
    required String paymentStatus,
    required String? customerName,
    required String? phoneNumber,
    required String? qid,
    required List<Map<String, dynamic>> items,
  }) async {
    _setLoading(true);
    try {
      final invoice = await _service.createInvoice(
        plateNumber: plateNumber,
        laborCharges: laborCharges,
        paymentStatus: paymentStatus,
        customerName: customerName,
        phoneNumber: phoneNumber,
        qid: qid,
        items: items,
      );
      
      if (invoice != null) {
        final summary = InsuranceInvoiceSummary(
          customerId: invoice.customerId,
          name: invoice.customer.customerName,
          phoneNumber: invoice.customer.phoneNumber,
          invoiceId: invoice.id,
          plateNumber: invoice.plateNumber,
          paymentStatus: invoice.paymentStatus,
          invoiceDate: invoice.createdAt,
        );
        _invoices.insert(0, summary);
        _total += 1;
        notifyListeners();
      }
      
      return invoice;
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
      return null;
    } catch (e) {
      _errorMessage = 'Failed to create invoice.';
      notifyListeners();
      return null;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> updateInvoice(int invoiceId, Map<String, dynamic> fields) async {
    try {
      await _service.updateInvoice(invoiceId, fields);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Failed to update invoice.';
      notifyListeners();
    }
  }

  Future<void> updateCustomer(int customerId, Map<String, dynamic> fields) async {
    try {
      await _service.updateCustomer(customerId, fields);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Failed to update customer.';
      notifyListeners();
    }
  }

  Future<void> updateItem(int itemId, Map<String, dynamic> fields) async {
    try {
      await _service.updateItem(itemId, fields);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Failed to update item.';
      notifyListeners();
    }
  }

  Future<InsuranceItem?> createItem(int invoiceId, Map<String, dynamic> fields) async {
    try {
      return await _service.createItem(invoiceId, fields);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
      return null;
    } catch (_) {
      _errorMessage = 'Failed to create item.';
      notifyListeners();
      return null;
    }
  }

  Future<void> deleteItem(int itemId) async {
    try {
      await _service.deleteItem(itemId);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Failed to delete item.';
      notifyListeners();
    }
  }

  Future<void> deleteImage(int imageId) async {
    try {
      await _service.deleteImage(imageId);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Failed to delete image.';
      notifyListeners();
    }
  }

  Future<InsuranceImage?> uploadImage({
    required int invoiceId,
    required String imageType,
    required String filename,
    required List<int> bytes,
  }) async {
    try {
      return await _service.uploadImage(
        invoiceId: invoiceId,
        imageType: imageType,
        filename: filename,
        bytes: bytes,
      );
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
      return null;
    } catch (_) {
      _errorMessage = 'Failed to upload image.';
      notifyListeners();
      return null;
    }
  }

  Future<void> deleteInvoice(int invoiceId) async {
    final index = _invoices.indexWhere((i) => i.invoiceId == invoiceId);
    InsuranceInvoiceSummary? removed;
    if (index != -1) {
      removed = _invoices.removeAt(index);
      notifyListeners();
    }
    try {
      await _service.deleteInvoice(invoiceId);
    } catch (e) {
      if (removed != null) _invoices.insert(index, removed);
      _errorMessage = 'Failed to delete invoice.';
      notifyListeners();
    }
  }

  void clearError() {
    if (_errorMessage != null) {
      _errorMessage = null;
      notifyListeners();
    }
  }

  void _setLoading(bool v) {
    _isLoading = v;
    if (v) _errorMessage = null;
    notifyListeners();
  }
}
