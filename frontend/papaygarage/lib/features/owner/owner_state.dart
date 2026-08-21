import 'package:flutter/material.dart';
import '../../core/api/api_client.dart';
import '../../core/api/api_endpoints.dart';

// ─────────────────────────────────────────────────────────────
// Data models mirroring the backend response
// ─────────────────────────────────────────────────────────────

class InvoiceProfitBreakdown {
  final double total;
  final double paid;
  final double unpaid;
  const InvoiceProfitBreakdown({required this.total, required this.paid, required this.unpaid});

  factory InvoiceProfitBreakdown.fromJson(Map<String, dynamic> j) =>
      InvoiceProfitBreakdown(
        total: _d(j['total']),
        paid: _d(j['paid']),
        unpaid: _d(j['unpaid']),
      );
}

class UtilityExpense {
  final double internet;
  final double electricity;
  final double water;
  final double total;
  const UtilityExpense({required this.internet, required this.electricity, required this.water, required this.total});

  factory UtilityExpense.fromJson(Map<String, dynamic> j) => UtilityExpense(
        internet: _d(j['INTERNET']),
        electricity: _d(j['ELECTRICITY']),
        water: _d(j['WATER']),
        total: _d(j['total']),
      );
}

class SalaryEntry {
  final String name;
  final double amount;
  const SalaryEntry({required this.name, required this.amount});

  factory SalaryEntry.fromJson(Map<String, dynamic> j) =>
      SalaryEntry(name: j['name'] as String, amount: _d(j['amount']));
}

class SalaryExpense {
  final List<SalaryEntry> employees;
  final double total;
  const SalaryExpense({required this.employees, required this.total});

  factory SalaryExpense.fromJson(Map<String, dynamic> j) => SalaryExpense(
        employees: (j['employees'] as List)
            .map((e) => SalaryEntry.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: _d(j['total']),
      );
}

class MonthlySummary {
  final int year;
  final int month;

  final InvoiceProfitBreakdown insuranceProfit;
  final InvoiceProfitBreakdown mechanicProfit;
  final double partsProfit;

  final double productExpense;
  final double rentExpense;
  final UtilityExpense utilityExpense;
  final SalaryExpense salaryExpense;
  final double garageExpense;

  final double totalProfit;
  final double totalExpense;
  final double net;

  const MonthlySummary({
    required this.year,
    required this.month,
    required this.insuranceProfit,
    required this.mechanicProfit,
    required this.partsProfit,
    required this.productExpense,
    required this.rentExpense,
    required this.utilityExpense,
    required this.salaryExpense,
    required this.garageExpense,
    required this.totalProfit,
    required this.totalExpense,
    required this.net,
  });

  factory MonthlySummary.fromJson(Map<String, dynamic> j) => MonthlySummary(
        year: j['year'] as int,
        month: j['month'] as int,
        insuranceProfit: InvoiceProfitBreakdown.fromJson(j['insurance_profit']),
        mechanicProfit: InvoiceProfitBreakdown.fromJson(j['mechanic_profit']),
        partsProfit: _d(j['parts_profit']),
        productExpense: _d(j['product_expense']),
        rentExpense: _d(j['rent_expense']),
        utilityExpense: UtilityExpense.fromJson(j['utility_expense']),
        salaryExpense: SalaryExpense.fromJson(j['salary_expense']),
        garageExpense: _d(j['garage_expense']),
        totalProfit: _d(j['total_profit']),
        totalExpense: _d(j['total_expense']),
        net: _d(j['net']),
      );
}

double _d(dynamic v) {
  if (v == null) return 0.0;
  return double.tryParse(v.toString()) ?? 0.0;
}

// ─────────────────────────────────────────────────────────────
// State provider
// ─────────────────────────────────────────────────────────────

class OwnerState extends ChangeNotifier {
  final ApiClient _api;

  OwnerState({required ApiClient apiClient}) : _api = apiClient;

  MonthlySummary? _summary;
  bool _loading = false;
  String? _error;

  MonthlySummary? get summary => _summary;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> fetchSummary(int year, int month) async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _api.get('${ApiEndpoints.summary}/$year/$month');
      _summary = MonthlySummary.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}
