import 'package:flutter/material.dart';
import '../services/records_service.dart';

class RecordsState extends ChangeNotifier {
  final RecordsService _recordsService;

  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  bool get isLoadingMore => _isLoadingMore;
  String? get errorMessage => _errorMessage;

  static const int _pageSize = 10;

  // Saved records per category
  List<dynamic> _products = [];
  List<dynamic> _rents = [];
  List<dynamic> _salaries = [];
  List<dynamic> _utilityBills = [];
  List<dynamic> _profits = [];
  List<dynamic> _expenses = [];

  List<dynamic> get products => _products;
  List<dynamic> get rents => _rents;
  List<dynamic> get salaries => _salaries;
  List<dynamic> get utilityBills => _utilityBills;
  List<dynamic> get profits => _profits;
  List<dynamic> get expenses => _expenses;

  // hasMore flags per category
  bool _hasMoreProducts = false;
  bool _hasMoreRents = false;
  bool _hasMoreSalaries = false;
  bool _hasMoreUtilityBills = false;
  bool _hasMoreProfits = false;
  bool _hasMoreExpenses = false;

  bool get hasMoreProducts => _hasMoreProducts;
  bool get hasMoreRents => _hasMoreRents;
  bool get hasMoreSalaries => _hasMoreSalaries;
  bool get hasMoreUtilityBills => _hasMoreUtilityBills;
  bool get hasMoreProfits => _hasMoreProfits;
  bool get hasMoreExpenses => _hasMoreExpenses;

  bool hasMoreFor(String catId) {
    switch (catId) {
      case 'products': return _hasMoreProducts;
      case 'rent':     return _hasMoreRents;
      case 'salary':   return _hasMoreSalaries;
      case 'utility':  return _hasMoreUtilityBills;
      case 'profit':   return _hasMoreProfits;
      case 'expense':  return _hasMoreExpenses;
      default:         return false;
    }
  }

  // Date filters for Salary and Utility Bills
  int _currentYear = DateTime.now().year;
  int _currentMonth = DateTime.now().month;

  int get currentYear => _currentYear;
  int get currentMonth => _currentMonth;

  RecordsState({required RecordsService recordsService})
      : _recordsService = recordsService;

  void setMonthYearForSalaries(int year, int month) {
    _currentYear = year;
    _currentMonth = month;
    fetchSalaries();
  }

  void setMonthYearForUtility(int year, int month) {
    _currentYear = year;
    _currentMonth = month;
    fetchUtilityBills();
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String? error) {
    _errorMessage = error;
    notifyListeners();
  }

  // --- Initial Fetch Methods (resets to first 10) ---

  Future<void> fetchProducts() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getProducts(limit: _pageSize, offset: 0);
      _products = data;
      _hasMoreProducts = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchRents() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getRents(limit: _pageSize, offset: 0);
      _rents = data;
      _hasMoreRents = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchSalaries() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getSalaries(_currentYear, _currentMonth, limit: _pageSize, offset: 0);
      _salaries = data;
      _hasMoreSalaries = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchUtilityBills() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getUtilityBills(_currentYear, _currentMonth, limit: _pageSize, offset: 0);
      _utilityBills = data;
      _hasMoreUtilityBills = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchProfits() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getProfits(limit: _pageSize, offset: 0);
      _profits = data;
      _hasMoreProfits = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<void> fetchExpenses() async {
    _setLoading(true);
    _setError(null);
    try {
      final data = await _recordsService.getExpenses(limit: _pageSize, offset: 0);
      _expenses = data;
      _hasMoreExpenses = data.length == _pageSize;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // --- Load More Methods (append next 10) ---

  Future<void> loadMoreProducts() async {
    if (!_hasMoreProducts || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _recordsService.getProducts(limit: _pageSize, offset: _products.length);
      _products.addAll(data);
      _hasMoreProducts = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreRents() async {
    if (!_hasMoreRents || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _recordsService.getRents(limit: _pageSize, offset: _rents.length);
      _rents.addAll(data);
      _hasMoreRents = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreSalaries() async {
    if (!_hasMoreSalaries || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _recordsService.getSalaries(_currentYear, _currentMonth, limit: _pageSize, offset: _salaries.length);
      _salaries.addAll(data);
      _hasMoreSalaries = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreUtilityBills() async {
    if (!_hasMoreUtilityBills || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _recordsService.getUtilityBills(_currentYear, _currentMonth, limit: _pageSize, offset: _utilityBills.length);
      _utilityBills.addAll(data);
      _hasMoreUtilityBills = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreProfits() async {
    if (!_hasMoreProfits || _isLoadingMore) return;
    _isLoadingMore = true;
    notifyListeners();
    try {
      final data = await _recordsService.getProfits(limit: _pageSize, offset: _profits.length);
      _profits.addAll(data);
      _hasMoreProfits = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
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
      final data = await _recordsService.getExpenses(limit: _pageSize, offset: _expenses.length);
      _expenses.addAll(data);
      _hasMoreExpenses = data.length == _pageSize;
    } catch (e) {
      _setError(e.toString());
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  Future<void> loadMoreFor(String catId) async {
    switch (catId) {
      case 'products': await loadMoreProducts();     break;
      case 'rent':     await loadMoreRents();        break;
      case 'salary':   await loadMoreSalaries();     break;
      case 'utility':  await loadMoreUtilityBills(); break;
      case 'profit':   await loadMoreProfits();      break;
      case 'expense':  await loadMoreExpenses();     break;
    }
  }

  // --- Create Methods ---

  Future<bool> saveProducts(List<Map<String, dynamic>> rows) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        if (row['description'] == null || row['description'].isEmpty) continue;
        await _recordsService.createProduct({
          'description': row['description'],
          'quantity': int.tryParse(row['quantity']?.toString() ?? '1') ?? 1,
          'unit_price': double.tryParse(row['unit_price']?.toString() ?? '0') ?? 0.0,
        });
      }
      notifyListeners();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> saveRents(List<Map<String, dynamic>> rows, DateTime date) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        final amount = double.tryParse(row['amount']?.toString() ?? '0') ?? 0.0;
        if (amount <= 0) continue;
        await _recordsService.createRent({
          'amount': amount,
          'year': date.year,
          'month': date.month,
        });
      }
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> saveSalaries(List<Map<String, dynamic>> rows) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        if (row['name'] == null || row['name'].isEmpty) continue;
        await _recordsService.createSalary({
          'name': row['name'],
          'amount': double.tryParse(row['amount']?.toString() ?? '0') ?? 0.0,
        });
      }
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> saveUtilityBills(List<Map<String, dynamic>> rows, DateTime date) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        final amount = double.tryParse(row['amount']?.toString() ?? '0') ?? 0.0;
        if (amount <= 0) continue;
        await _recordsService.createUtilityBill({
          'bill_type': row['bill_type'] ?? 'ELECTRICITY',
          'amount': amount,
          'year': date.year,
          'month': date.month,
        });
      }
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> saveProfits(List<Map<String, dynamic>> rows) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        if (row['name'] == null || row['name'].isEmpty) continue;
        await _recordsService.createProfit({
          'name': row['name'],
          'amount': double.tryParse(row['amount']?.toString() ?? '0') ?? 0.0,
        });
      }
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> saveExpenses(List<Map<String, dynamic>> rows) async {
    _setLoading(true);
    _setError(null);
    try {
      for (final row in rows) {
        if (row['description'] == null || row['description'].isEmpty) continue;
        await _recordsService.createExpense({
          'description': row['description'],
          'amount': double.tryParse(row['amount']?.toString() ?? '0') ?? 0.0,
        });
      }
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // --- Delete Methods (Optimistic UI) ---

  Future<void> deleteProduct(int id) async {
    final backup = List<dynamic>.from(_products);
    _products.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteProduct(id);
    } catch (e) {
      _products = backup;
      _setError(e.toString());
    }
  }

  Future<void> deleteRent(int id) async {
    final backup = List<dynamic>.from(_rents);
    _rents.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteRent(id);
    } catch (e) {
      _rents = backup;
      _setError(e.toString());
    }
  }

  Future<void> deleteSalary(int id) async {
    final backup = List<dynamic>.from(_salaries);
    _salaries.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteSalary(id);
    } catch (e) {
      _salaries = backup;
      _setError(e.toString());
    }
  }

  Future<void> deleteUtilityBill(int id) async {
    final backup = List<dynamic>.from(_utilityBills);
    _utilityBills.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteUtilityBill(id);
    } catch (e) {
      _utilityBills = backup;
      _setError(e.toString());
    }
  }

  Future<void> deleteProfit(int id) async {
    final backup = List<dynamic>.from(_profits);
    _profits.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteProfit(id);
    } catch (e) {
      _profits = backup;
      _setError(e.toString());
    }
  }

  Future<void> deleteExpense(int id) async {
    final backup = List<dynamic>.from(_expenses);
    _expenses.removeWhere((e) => e['id'] == id);
    notifyListeners();
    try {
      await _recordsService.deleteExpense(id);
    } catch (e) {
      _expenses = backup;
      _setError(e.toString());
    }
  }
}
