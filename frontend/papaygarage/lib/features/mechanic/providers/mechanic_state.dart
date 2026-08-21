import 'package:flutter/foundation.dart';
import '../../../core/api/api_exception.dart';
import '../models/mechanic_models.dart';
import '../services/mechanic_service.dart';

class MechanicState extends ChangeNotifier {
  final MechanicService _service;

  MechanicState({required MechanicService service}) : _service = service;

  bool _isLoading = false;
  String? _errorMessage;
  List<MechanicInvoiceSummary> _invoices = [];
  
  // Pagination & Filtering
  int _offset = 0;
  final int _limit = 20;
  String? _plateFilter;
  String? _startDateFilter;
  String? _endDateFilter;
  bool _hasMore = true;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<MechanicInvoiceSummary> get invoices => _invoices;
  bool get hasMore => _hasMore;

  int _currentPage = 1;
  int get currentPage => _currentPage;
  bool get canGoNext => _hasMore;
  bool get canGoPrev => _currentPage > 1;

  void setFilters({String? plate, String? startDate, String? endDate}) {
    _plateFilter = plate;
    _startDateFilter = startDate;
    _endDateFilter = endDate;
    _offset = 0;
    _currentPage = 1;
    _invoices = [];
    _hasMore = true;
    fetchInvoices();
  }

  Future<void> fetchInvoices() async {
    if (_isLoading) return;
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final results = await _service.getInvoices(
        limit: _limit,
        offset: _offset,
        plateNumber: _plateFilter,
        startDate: _startDateFilter,
        endDate: _endDateFilter,
      );

      _hasMore = results.length == _limit;
      _invoices = results;
    } on ApiException catch (e) {
      _errorMessage = e.message;
    } catch (_) {
      _errorMessage = 'An unexpected error occurred while fetching invoices.';
    } finally {
      _isLoading = false;
      notifyListeners();
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

  Future<MechanicInvoice?> getInvoice(int invoiceId) async {
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

  Future<MechanicInvoice?> createInvoice({
    required String plateNumber,
    required double laborCharges,
    required PaymentStatus paymentStatus,
    required String? customerName,
    required String? phoneNumber,
    required String? qid,
    required List<Map<String, dynamic>> items,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final invoice = await _service.createInvoice(
        plateNumber: plateNumber,
        laborCharges: laborCharges,
        paymentStatus: paymentStatusLabel(paymentStatus),
        customerName: customerName,
        phoneNumber: phoneNumber,
        qid: qid,
        items: items,
      );
      
      final summary = MechanicInvoiceSummary(
        invoiceId: invoice.id,
        plateNumber: invoice.plateNumber,
        name: invoice.customer.customerName,
        paymentStatus: invoice.paymentStatus,
        invoiceDate: invoice.invoiceDate,
      );
      _invoices.insert(0, summary);
      
      return invoice;
    } on ApiException catch (e) {
      _errorMessage = e.message;
      return null;
    } catch (_) {
      _errorMessage = 'Failed to create invoice.';
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<MechanicInvoice?> updateInvoice(int invoiceId, Map<String, dynamic> fields) async {
    try {
      return await _service.updateInvoice(invoiceId, fields);
    } on ApiException catch (e) {
      _errorMessage = e.message;
      notifyListeners();
      return null;
    } catch (_) {
      _errorMessage = 'Failed to update invoice.';
      notifyListeners();
      return null;
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

  Future<MechanicItem?> createItem(int invoiceId, Map<String, dynamic> fields) async {
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

  Future<void> deleteInvoice(int invoiceId) async {
    final index = _invoices.indexWhere((i) => i.invoiceId == invoiceId);
    MechanicInvoiceSummary? removed;
    if (index != -1) {
      removed = _invoices.removeAt(index);
      notifyListeners();
    }

    try {
      await _service.deleteInvoice(invoiceId);
    } on ApiException catch (e) {
      if (removed != null) {
        _invoices.insert(index, removed);
      }
      _errorMessage = e.message;
      notifyListeners();
    } catch (_) {
      if (removed != null) {
        _invoices.insert(index, removed);
      }
      _errorMessage = 'Failed to delete invoice.';
      notifyListeners();
    }
  }
}
