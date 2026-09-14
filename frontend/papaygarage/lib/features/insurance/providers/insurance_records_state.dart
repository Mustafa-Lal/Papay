import 'package:flutter/material.dart';
import '../models/insurance_models.dart';
import '../services/insurance_records_service.dart';

class InsuranceRecordsState extends ChangeNotifier {
  final InsuranceRecordsService _service;

  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  bool get isLoadingMore => _isLoadingMore;
  String? get errorMessage => _errorMessage;

  static const int _pageSize = 10;

  List<dynamic> _incomes = [];
  List<dynamic> _expenses = [];

  List<dynamic> get incomes => _incomes;
  List<dynamic> get expenses => _expenses;

  bool _hasMoreIncomes = false;
  bool _hasMoreExpenses = false;

  bool get hasMoreIncomes => _hasMoreIncomes;
  bool get hasMoreExpenses => _hasMoreExpenses;

  // Report state
  InsuranceFinanceReport? _report;
  bool _isLoadingReport = false;
  String? _reportErrorMessage;
  DateTime? _reportStartDate;
  DateTime? _reportEndDate;

  InsuranceFinanceReport? get report => _report;
  bool get isLoadingReport => _isLoadingReport;
  String? get reportErrorMessage => _reportErrorMessage;
  DateTime? get reportStartDate => _reportStartDate;
  DateTime? get reportEndDate => _reportEndDate;

  bool hasMoreFor(String catId) {
    switch (catId) {
      case 'income':
        return _hasMoreIncomes;
      case 'expense':
        return _hasMoreExpenses;
      default:
        return false;
    }
  }

  InsuranceRecordsState({required InsuranceRecordsService service})
      : _service = service;


  // ---------------------------------------------------------------------------
  // Fetch
  // ---------------------------------------------------------------------------

  Future<void> fetchIncomes() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      final data = await _service.getIncomes(limit: _pageSize, offset: 0);
      _incomes = data;
      _hasMoreIncomes = data.length == _pageSize;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchExpenses() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      final data = await _service.getExpenses(limit: _pageSize, offset: 0);
      _expenses = data;
      _hasMoreExpenses = data.length == _pageSize;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ---------------------------------------------------------------------------
  // Pagination
  // ---------------------------------------------------------------------------

  Future<void> loadMoreIncomes() async {
    if (!_hasMoreIncomes || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _service.getIncomes(limit: _pageSize, offset: _incomes.length);
      _incomes.addAll(data);
      _hasMoreIncomes = data.length == _pageSize;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreExpenses() async {
    if (!_hasMoreExpenses || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _service.getExpenses(limit: _pageSize, offset: _expenses.length);
      _expenses.addAll(data);
      _hasMoreExpenses = data.length == _pageSize;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreFor(String catId) async {
    switch (catId) {
      case 'income':
        await loadMoreIncomes();
        break;
      case 'expense':
        await loadMoreExpenses();
        break;
    }
  }

  // ---------------------------------------------------------------------------
  // Save Records (batch of newly created rows)
  // ---------------------------------------------------------------------------

  Future<bool> saveIncomes(List<Map<String, dynamic>> rows) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      for (final r in rows) {
        final price = double.tryParse(r['price']?.toString() ?? '0') ?? 0.0;
        await _service.createIncome({
          'description': (r['description'] ?? '').toString().trim(),
          'price': price.toStringAsFixed(2),
        });
      }
      await fetchIncomes();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> saveExpenses(List<Map<String, dynamic>> rows) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      for (final r in rows) {
        final price = double.tryParse(r['price']?.toString() ?? '0') ?? 0.0;
        await _service.createExpense({
          'description': (r['description'] ?? '').toString().trim(),
          'price': price.toStringAsFixed(2),
        });
      }
      await fetchExpenses();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // ---------------------------------------------------------------------------
  // Delete
  // ---------------------------------------------------------------------------

  Future<void> deleteIncome(int id) async {
    final backup = List<dynamic>.from(_incomes);
    _incomes.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _service.deleteIncome(id);
    } catch (e) {
      _incomes = backup;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }

  Future<void> deleteExpense(int id) async {
    final backup = List<dynamic>.from(_expenses);
    _expenses.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _service.deleteExpense(id);
    } catch (e) {
      _expenses = backup;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }

  // ---------------------------------------------------------------------------
  // Update
  // ---------------------------------------------------------------------------

  Future<bool> updateIncome(int id, Map<String, dynamic> data) async {
    final backup = List<dynamic>.from(_incomes);
    final idx = _incomes.indexWhere((e) => e['id'] == id);
    if (idx != -1) {
      final updated = Map<String, dynamic>.from(_incomes[idx] as Map<String, dynamic>)..addAll(data);
      _incomes[idx] = updated;
      notifyListeners();
    }
    try {
      await _service.updateIncome(id, data);
      return true;
    } catch (e) {
      _incomes = backup;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateExpense(int id, Map<String, dynamic> data) async {
    final backup = List<dynamic>.from(_expenses);
    final idx = _expenses.indexWhere((e) => e['id'] == id);
    if (idx != -1) {
      final updated = Map<String, dynamic>.from(_expenses[idx] as Map<String, dynamic>)..addAll(data);
      _expenses[idx] = updated;
      notifyListeners();
    }
    try {
      await _service.updateExpense(id, data);
      return true;
    } catch (e) {
      _expenses = backup;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  // ---------------------------------------------------------------------------
  // Report
  // ---------------------------------------------------------------------------

  void setReportDateRange(DateTime? start, DateTime? end) {
    _reportStartDate = start;
    _reportEndDate = end;
    notifyListeners();
  }

  Future<void> fetchReport({DateTime? start, DateTime? end}) async {
    _isLoadingReport = true;
    _reportErrorMessage = null;
    if (start != null || end != null) {
      _reportStartDate = start;
      _reportEndDate = end;
    }
    notifyListeners();
    try {
      final res = await _service.getFinanceReport(
        startDate: _reportStartDate,
        endDate: _reportEndDate,
      );
      _report = res;
    } catch (e) {
      _reportErrorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoadingReport = false;
      notifyListeners();
    }
  }
}

