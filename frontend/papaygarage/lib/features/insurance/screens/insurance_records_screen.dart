import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'dart:math';

import '../../mechanic/models/record_models.dart';
import '../models/insurance_models.dart';
import '../providers/insurance_records_state.dart';
import '../utils/insurance_finance_report_printer.dart';

// ─── Design Tokens ───────────────────────────────────────────────────────────
const _ink = Color(0xFF1C1812);
const _muted = Color(0xFF9A9080);
const _border = Color(0xFFE8E1D4);
const _bg = Color(0xFFEEE9DF);
const _card = Color(0xFFFFFFFF);
const _inputBg = Color(0xFFFCFBF8);

const _gold = Color(0xFFB8863A);
const _goldDark = Color(0xFF9A6E28);
const _goldTint = Color(0xFFF3E2B8);
const _goldSoft = Color(0xFFFBF2DD);

const _compactBreakpoint = 840.0;
bool _isCompact(BuildContext context) => MediaQuery.sizeOf(context).width < _compactBreakpoint;

// ─── Category Definitions ────────────────────────────────────────────────────
final _insuranceCategories = [
  const RecordCategory(
    id: 'income',
    label: 'Income',
    icon: 'trending-up',
    color: 0xFFB8863A,
    softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(
        key: 'description',
        label: 'Source / Description',
        type: 'text',
        flex: 2.0,
        placeholder: 'e.g. Insurance claim payout',
      ),
      RecordColumn(
        key: 'price',
        label: 'Price (QR)',
        type: 'number',
        flex: 1.0,
        placeholder: '0.00',
      ),
    ],
  ),
  const RecordCategory(
    id: 'expense',
    label: 'Expense',
    icon: 'trending-down',
    color: 0xFFB8863A,
    softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(
        key: 'description',
        label: 'Description',
        type: 'text',
        flex: 2.0,
        placeholder: 'e.g. Towing / Parts recovery',
      ),
      RecordColumn(
        key: 'price',
        label: 'Price (QR)',
        type: 'number',
        flex: 1.0,
        placeholder: '0.00',
      ),
    ],
  ),
  const RecordCategory(
    id: 'report',
    label: 'Report & Print',
    icon: 'receipt-long',
    color: 0xFFB8863A,
    softColor: 0xFFF3E2B8,
    columns: [],
  ),
];

Map<String, dynamic> _emptyRow(RecordCategory cat) {
  final row = <String, dynamic>{
    'id': '${DateTime.now().millisecondsSinceEpoch}${Random().nextInt(9999)}',
  };
  for (final c in cat.columns) {
    row[c.key] = '';
  }
  return row;
}

double _rowTotal(Map<String, dynamic> row) {
  return double.tryParse(row['price']?.toString() ?? '0') ?? 0;
}

// ─── Screen ──────────────────────────────────────────────────────────────────
class InsuranceRecordsScreen extends StatefulWidget {
  const InsuranceRecordsScreen({super.key});

  @override
  State<InsuranceRecordsScreen> createState() => _InsuranceRecordsScreenState();
}

class _InsuranceRecordsScreenState extends State<InsuranceRecordsScreen>
    with TickerProviderStateMixin {
  String _activeId = 'income';

  final Map<String, List<Map<String, dynamic>>> _draftRows = {};
  final Map<String, bool> _savedExpanded = {};

  late AnimationController _tabAnimCtrl;
  late Animation<double> _tabAnim;

  @override
  void initState() {
    super.initState();
    for (final cat in _insuranceCategories) {
      _draftRows[cat.id] = [_emptyRow(cat)];
      _savedExpanded[cat.id] = false;
    }
    _tabAnimCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 220));
    _tabAnim = CurvedAnimation(parent: _tabAnimCtrl, curve: Curves.easeOut);
    _tabAnimCtrl.forward();
  }

  @override
  void dispose() {
    _tabAnimCtrl.dispose();
    super.dispose();
  }

  RecordCategory get _cat => _insuranceCategories.firstWhere((c) => c.id == _activeId);
  Color get _cCol => Color(_cat.color);
  Color get _sCol => Color(_cat.softColor);

  void _switchTab(String id) {
    if (id == _activeId) return;
    setState(() => _activeId = id);
    _tabAnimCtrl
      ..reset()
      ..forward();
    if (id == 'report') {
      final st = context.read<InsuranceRecordsState>();
      if (st.report == null) {
        st.fetchReport();
      }
    }
  }

  void _updateRow(String rowId, String key, String val) {
    setState(() {
      final rows = _draftRows[_activeId]!;

      final idx = rows.indexWhere((r) => r['id'] == rowId);
      if (idx != -1) rows[idx][key] = val;
    });
  }

  void _addRow() => setState(() => _draftRows[_activeId]!.add(_emptyRow(_cat)));

  void _removeRow(String id) => setState(() {
        final rows = _draftRows[_activeId]!;
        rows.removeWhere((r) => r['id'] == id);
        if (rows.isEmpty) rows.add(_emptyRow(_cat));
      });

  Future<void> _save() async {
    final st = context.read<InsuranceRecordsState>();
    final cat = _cat;
    final rows = List<Map<String, dynamic>>.from(_draftRows[_activeId]!);

    for (final row in rows) {
      final desc = row['description']?.toString().trim() ?? '';
      final priceStr = row['price']?.toString().trim() ?? '';
      if (desc.isEmpty) {
        _showToast('${cat.label} description is required.', success: false);
        return;
      }
      if (priceStr.isEmpty || double.tryParse(priceStr) == null || double.parse(priceStr) < 0) {
        _showToast('A valid ${cat.label.toLowerCase()} price is required.', success: false);
        return;
      }
    }

    bool ok = false;
    switch (cat.id) {
      case 'income':
        ok = await st.saveIncomes(rows);
        break;
      case 'expense':
        ok = await st.saveExpenses(rows);
        break;
    }

    if (!mounted) return;
    if (ok) {
      _showToast('${cat.label} saved successfully!', success: true);
      setState(() {
        _draftRows[_activeId] = [_emptyRow(cat)];
      });
    } else {
      _showToast(st.errorMessage ?? 'Error saving records', success: false);
    }
  }

  Future<void> _edit(Map<String, dynamic> item) async {
    final cat = _cat;
    final id = item['id'] as int;
    final result = await _showEditDialog(cat, item);
    if (result == null || !mounted) return;
    final st = context.read<InsuranceRecordsState>();
    bool ok = false;
    switch (cat.id) {
      case 'income':
        ok = await st.updateIncome(id, result);
        break;
      case 'expense':
        ok = await st.updateExpense(id, result);
        break;
    }
    if (!mounted) return;
    _showToast(ok ? '${cat.label} updated!' : (st.errorMessage ?? 'Update failed'), success: ok);
  }

  Future<Map<String, dynamic>?> _showEditDialog(
      RecordCategory cat, Map<String, dynamic> item) async {
    final controllers = <String, TextEditingController>{};
    for (final col in cat.columns) {
      final val = item[col.key]?.toString() ?? '';
      controllers[col.key] = TextEditingController(text: val);
    }

    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) {
          return Dialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
            child: Container(
              width: 400,
              constraints: BoxConstraints(maxWidth: MediaQuery.sizeOf(ctx).width - 40),
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                            color: _goldSoft, borderRadius: BorderRadius.circular(12)),
                        child: const Icon(Icons.edit_rounded, color: _gold, size: 20),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Edit ${cat.label}',
                              style: GoogleFonts.oswald(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: _ink,
                                  letterSpacing: 0.2),
                            ),
                            Text('Update the details below',
                                style: GoogleFonts.inter(fontSize: 13, color: _muted)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  ...cat.columns.map((col) => Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              col.label.toUpperCase(),
                              style: GoogleFonts.oswald(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 0.9,
                                  color: _muted),
                            ),
                            const SizedBox(height: 7),
                            TextField(
                              controller: controllers[col.key],
                              keyboardType: col.type == 'number'
                                  ? const TextInputType.numberWithOptions(decimal: true)
                                  : TextInputType.text,
                              style: GoogleFonts.inter(
                                  fontSize: 14, color: _ink, fontWeight: FontWeight.w500),
                              decoration: InputDecoration(
                                hintText: col.placeholder,
                                hintStyle: GoogleFonts.inter(
                                    color: const Color(0xFFB8B0A4), fontSize: 14),
                                filled: true,
                                fillColor: _inputBg,
                                contentPadding:
                                    const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                                enabledBorder: OutlineInputBorder(
                                    borderSide: const BorderSide(color: _border, width: 1.5),
                                    borderRadius: BorderRadius.circular(10)),
                                focusedBorder: OutlineInputBorder(
                                    borderSide: const BorderSide(color: _gold, width: 1.8),
                                    borderRadius: BorderRadius.circular(10)),
                              ),
                            ),
                          ],
                        ),
                      )),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => Navigator.pop(ctx, null),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: _border, width: 1.5),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            foregroundColor: _ink,
                          ),
                          child: Text('Cancel',
                              style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            final payload = <String, dynamic>{};
                            for (final col in cat.columns) {
                              final text = controllers[col.key]!.text.trim();
                              if (col.type == 'number') {
                                final numVal = double.tryParse(text);
                                if (numVal == null || numVal < 0) {
                                  _showToast('Please enter a valid price.', success: false);
                                  return;
                                }
                                payload[col.key] = numVal.toStringAsFixed(2);
                              } else {
                                if (text.isEmpty) {
                                  _showToast('${col.label} is required.', success: false);
                                  return;
                                }
                                payload[col.key] = text;
                              }
                            }
                            Navigator.pop(ctx, payload);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _gold,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                          child: Text('Save Changes',
                              style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );

    for (final c in controllers.values) {
      c.dispose();
    }
    return result;
  }

  Future<void> _delete(int id) async {
    final confirmed = await _confirmDelete();
    if (!confirmed || !mounted) return;
    final st = context.read<InsuranceRecordsState>();
    switch (_cat.id) {
      case 'income':
        await st.deleteIncome(id);
        break;
      case 'expense':
        await st.deleteExpense(id);
        break;
    }
    if (!mounted) return;
    _showToast('${_cat.label} deleted.', success: true);
  }

  Future<bool> _confirmDelete() async {
    return await showDialog<bool>(
          context: context,
          builder: (ctx) => Dialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            child: Container(
              width: 360,
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: const Color(0xFFFDECEB),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.delete_outline_rounded,
                            color: Color(0xFFC24C4A), size: 20),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Delete Record?',
                          style: GoogleFonts.oswald(
                              fontSize: 17, fontWeight: FontWeight.w600, color: _ink),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Are you sure you want to delete this record? This action cannot be undone.',
                    style: GoogleFonts.inter(fontSize: 13, color: _muted, height: 1.4),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => Navigator.pop(ctx, false),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: _border, width: 1.5),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                            padding: const EdgeInsets.symmetric(vertical: 13),
                            foregroundColor: _ink,
                          ),
                          child: Text('Cancel',
                              style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () => Navigator.pop(ctx, true),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFC24C4A),
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                            padding: const EdgeInsets.symmetric(vertical: 13),
                          ),
                          child: Text('Delete',
                              style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ) ??
        false;
  }

  void _showToast(String msg, {required bool success}) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Row(children: [
        Icon(success ? Icons.check_circle_rounded : Icons.error_rounded,
            color: Colors.white, size: 18),
        const SizedBox(width: 10),
        Expanded(
            child: Text(msg,
                style: GoogleFonts.inter(fontWeight: FontWeight.w600, color: Colors.white))),
      ]),
      backgroundColor: success ? const Color(0xFF4A8F6A) : const Color(0xFFC24C4A),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(16),
      duration: const Duration(seconds: 3),
    ));
  }

  void _fetchCurrent(InsuranceRecordsState st) {
    setState(() => _savedExpanded[_activeId] = true);
    switch (_activeId) {
      case 'income':
        st.fetchIncomes();
        break;
      case 'expense':
        st.fetchExpenses();
        break;
    }
  }

  IconData _icon(String name) {
    switch (name) {
      case 'trending-up':
        return Icons.trending_up_rounded;
      case 'trending-down':
        return Icons.trending_down_rounded;
      case 'receipt-long':
      case 'report':
        return Icons.receipt_long_rounded;
      default:
        return Icons.circle;
    }
  }

  Future<void> _pickReportDateRange() async {
    final st = context.read<InsuranceRecordsState>();
    final initialRange = (st.reportStartDate != null && st.reportEndDate != null)
        ? DateTimeRange(start: st.reportStartDate!, end: st.reportEndDate!)
        : null;

    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
      initialDateRange: initialRange,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: _gold,
              onPrimary: Colors.white,
              onSurface: _ink,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      st.fetchReport(start: picked.start, end: picked.end);
    }
  }

  void _applyQuickReportDate(String filter) {
    final st = context.read<InsuranceRecordsState>();
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    switch (filter) {
      case 'today':
        st.fetchReport(start: today, end: today);
        break;
      case 'week':
        final monday = today.subtract(Duration(days: today.weekday - 1));
        st.fetchReport(start: monday, end: today);
        break;
      case 'month':
        final firstOfMonth = DateTime(now.year, now.month, 1);
        st.fetchReport(start: firstOfMonth, end: today);
        break;
      case 'all':
        st.fetchReport(start: null, end: null);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final compact = _isCompact(context);
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: ScrollConfiguration(
          behavior: ScrollConfiguration.of(context).copyWith(scrollbars: false),
          child: SingleChildScrollView(
            padding: EdgeInsets.symmetric(
                horizontal: compact ? 16 : 44, vertical: compact ? 20 : 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildHeader(),
                const SizedBox(height: 28),
                _buildTabBar(),
                const SizedBox(height: 20),
                FadeTransition(
                  opacity: _tabAnim,
                  child: SlideTransition(
                    position: Tween<Offset>(begin: const Offset(0, 0.04), end: Offset.zero)
                        .animate(_tabAnim),
                    child: _buildMainCard(),
                  ),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final compact = _isCompact(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _GlassButton(
          onTap: () => Navigator.pop(context),
          child: const Icon(Icons.arrow_back_rounded, size: 20, color: _ink),
        ),
        SizedBox(width: compact ? 12 : 18),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Insurance Records',
                style: GoogleFonts.oswald(
                  fontSize: compact ? 22 : 26,
                  fontWeight: FontWeight.w600,
                  color: _ink,
                  letterSpacing: 0.2,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                'Track and record insurance claim incomes & expenses',
                style: GoogleFonts.inter(
                  fontSize: compact ? 12.5 : 13.5,
                  color: _muted,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTabBar() {
    final compact = _isCompact(context);
    Widget tab(RecordCategory cat) {
      final isActive = cat.id == _activeId;
      final cColor = Color(cat.color);
      return GestureDetector(
        onTap: () => _switchTab(cat.id),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
          margin: const EdgeInsets.symmetric(horizontal: 4),
          padding: EdgeInsets.symmetric(vertical: 15, horizontal: compact ? 8 : 16),
          decoration: BoxDecoration(
            color: isActive ? _card : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            boxShadow: isActive
                ? [
                    BoxShadow(
                        color: cColor.withValues(alpha: 0.18),
                        blurRadius: 12,
                        offset: const Offset(0, 4))
                  ]
                : [],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(_icon(cat.icon), size: 19, color: isActive ? cColor : _muted),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  cat.label,
                  style: GoogleFonts.oswald(
                    fontSize: 13.5,
                    fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
                    letterSpacing: 0.4,
                    color: isActive ? cColor : _muted,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: _goldTint,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: _insuranceCategories
            .map((cat) => Expanded(child: tab(cat)))
            .toList(),
      ),
    );
  }

  Widget _buildMainCard() {
    if (_activeId == 'report') {
      return _buildReportCard();
    }
    final pad = _isCompact(context) ? 16.0 : 24.0;
    return Container(
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border),
        boxShadow: const [
          BoxShadow(color: Color(0x0A000000), blurRadius: 32, offset: Offset(0, 8))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSectionBanner(
            'ADD NEW ${_cat.label.toUpperCase()}',
            _cCol,
            Icons.add_circle_outline_rounded,
          ),
          Padding(
            padding: EdgeInsets.fromLTRB(pad, 0, pad, pad),
            child: _buildDraftSection(),
          ),
          const Divider(height: 1, color: _border),
          _buildSectionBanner(
            'SAVED ${_cat.label.toUpperCase()}',
            _cCol,
            Icons.history_rounded,
          ),
          Padding(
            padding: EdgeInsets.fromLTRB(pad, 0, pad, pad),
            child: _buildSavedSection(),
          ),
        ],
      ),
    );
  }

  Widget _buildReportCard() {
    final pad = _isCompact(context) ? 16.0 : 24.0;
    final st = context.watch<InsuranceRecordsState>();
    final report = st.report;
    final loading = st.isLoadingReport;

    return Container(
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border),
        boxShadow: const [
          BoxShadow(color: Color(0x0A000000), blurRadius: 32, offset: Offset(0, 8))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildReportHeaderBanner(st, report),
          Padding(
            padding: EdgeInsets.all(pad),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildReportFilterBar(st),
                const SizedBox(height: 20),
                if (loading) ...[
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 48),
                    child: Center(
                      child: CircularProgressIndicator(color: _gold, strokeWidth: 2.5),
                    ),
                  ),
                ] else if (st.reportErrorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFDE8E8),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFF8B4B4)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline_rounded, color: Color(0xFFC81E1E), size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            st.reportErrorMessage!,
                            style: GoogleFonts.inter(
                              color: const Color(0xFF9B1C1C),
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: () => st.fetchReport(),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                ] else if (report != null) ...[
                  _buildReportSummaryKPIs(report),
                  const SizedBox(height: 24),
                  _buildReportLedgerPreview(report, st),
                ] else ...[
                  const _EmptyState(color: _gold),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReportHeaderBanner(InsuranceRecordsState st, InsuranceFinanceReport? report) {
    final compact = _isCompact(context);
    final titleWidget = Row(
      children: [
        const Icon(Icons.receipt_long_rounded, size: 20, color: _gold),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            'INSURANCE FINANCE REPORT & LEDGER',
            style: GoogleFonts.oswald(
              fontSize: compact ? 13 : 14,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.1,
              color: _gold,
            ),
          ),
        ),
      ],
    );

    final printBtn = report != null
        ? ElevatedButton.icon(
            onPressed: () => printInsuranceFinanceReport(
              context,
              report,
              startDate: st.reportStartDate,
              endDate: st.reportEndDate,
            ),
            icon: const Icon(Icons.print_rounded, size: 18, color: Colors.white),
            label: Text(
              'Print Ledger',
              style: GoogleFonts.oswald(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.6,
                color: Colors.white,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: _gold,
              foregroundColor: Colors.white,
              elevation: 0,
              minimumSize: const Size(0, 48),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          )
        : null;

    return Container(
      padding: EdgeInsets.symmetric(horizontal: compact ? 16 : 24, vertical: 14),
      decoration: BoxDecoration(
        color: _gold.withValues(alpha: 0.05),
        border: Border(bottom: BorderSide(color: _gold.withValues(alpha: 0.12))),
      ),
      child: compact && printBtn != null
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                titleWidget,
                const SizedBox(height: 12),
                printBtn,
              ],
            )
          : Row(
              children: [
                Expanded(child: titleWidget),
                if (printBtn != null) printBtn,
              ],
            ),
    );
  }

  Widget _buildReportFilterBar(InsuranceRecordsState st) {
    String rangeLabel = 'All Time';
    if (st.reportStartDate != null && st.reportEndDate != null) {
      final s = DateFormat('dd/MM/yyyy').format(st.reportStartDate!);
      final e = DateFormat('dd/MM/yyyy').format(st.reportEndDate!);
      rangeLabel = s == e ? s : '$s - $e';
    } else if (st.reportStartDate != null) {
      rangeLabel = 'From ${DateFormat('dd/MM/yyyy').format(st.reportStartDate!)}';
    } else if (st.reportEndDate != null) {
      rangeLabel = 'Until ${DateFormat('dd/MM/yyyy').format(st.reportEndDate!)}';
    }

    Widget quickPill(String label, String key) {
      return InkWell(
        onTap: () => _applyQuickReportDate(key),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFFF3EFE8),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: _border),
          ),
          child: Text(
            label,
            style: GoogleFonts.inter(fontSize: 12.5, fontWeight: FontWeight.w600, color: _ink),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF8F5),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Wrap(
            spacing: 10,
            runSpacing: 10,
            crossAxisAlignment: WrapCrossAlignment.center,
            alignment: WrapAlignment.spaceBetween,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  OutlinedButton.icon(
                    onPressed: _pickReportDateRange,
                    icon: const Icon(Icons.date_range_rounded, size: 18, color: _gold),
                    label: Text(
                      'Select Date Range',
                      style: GoogleFonts.inter(fontSize: 13.5, fontWeight: FontWeight.w600, color: _ink),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: _gold, width: 1.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      minimumSize: const Size(0, 48),
                      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                    ),
                  ),
                  const SizedBox(width: 8),
                  _GlassButton(
                    onTap: () => st.fetchReport(),
                    child: const Icon(Icons.refresh_rounded, size: 20, color: _ink),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: _goldSoft,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: _goldTint),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.calendar_today_rounded, size: 14, color: _goldDark),
                    const SizedBox(width: 6),
                    Text(
                      rangeLabel,
                      style: GoogleFonts.inter(
                        fontSize: 12.5,
                        fontWeight: FontWeight.w600,
                        color: _goldDark,
                      ),
                    ),
                    if (st.reportStartDate != null || st.reportEndDate != null) ...[
                      const SizedBox(width: 6),
                      InkWell(
                        onTap: () => st.fetchReport(start: null, end: null),
                        child: const Icon(Icons.close_rounded, size: 15, color: _goldDark),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text(
                'Quick filter:',
                style: GoogleFonts.inter(fontSize: 12, color: _muted, fontWeight: FontWeight.w500),
              ),
              quickPill('Today', 'today'),
              quickPill('This Week', 'week'),
              quickPill('This Month', 'month'),
              quickPill('All Time', 'all'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildReportSummaryKPIs(InsuranceFinanceReport report) {
    final compact = _isCompact(context);

    Widget kpiCard({
      required String title,
      required String amount,
      required String countSubtitle,
      required Color color,
      required Color bgColor,
      required IconData icon,
    }) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Row(
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w600,
                      color: _muted,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    amount,
                    style: GoogleFonts.oswald(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: _ink,
                    ),
                  ),
                  Text(
                    countSubtitle,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: _muted,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final isProfit = report.net >= 0;

    final cards = [
      kpiCard(
        title: 'TOTAL EXPENSES',
        amount: 'QR ${report.totalExpense.toStringAsFixed(2)}',
        countSubtitle: '${report.expenseCount} entries',
        color: const Color(0xFFC24C4A),
        bgColor: const Color(0xFFFDF4F4),
        icon: Icons.trending_down_rounded,
      ),
      kpiCard(
        title: 'TOTAL INCOME',
        amount: 'QR ${report.totalIncome.toStringAsFixed(2)}',
        countSubtitle: '${report.incomeCount} entries',
        color: const Color(0xFF3F8C58),
        bgColor: const Color(0xFFF3FAF5),
        icon: Icons.trending_up_rounded,
      ),
      kpiCard(
        title: isProfit ? 'NET PROFIT' : 'NET LOSS',
        amount: '${isProfit ? '+' : ''}${report.net.toStringAsFixed(2)} QR',
        countSubtitle: isProfit ? 'Positive balance' : 'Negative balance',
        color: isProfit ? _gold : const Color(0xFFC24C4A),
        bgColor: _goldSoft,
        icon: Icons.account_balance_wallet_rounded,
      ),
    ];

    if (compact) {
      return Column(
        children: cards.map((c) => Padding(padding: const EdgeInsets.only(bottom: 10), child: c)).toList(),
      );
    }

    return Row(
      children: cards
          .map((c) => Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 5),
                  child: c,
                ),
              ))
          .toList(),
    );
  }

  Widget _buildReportLedgerPreview(InsuranceFinanceReport report, InsuranceRecordsState st) {
    final expenses = report.expenses;
    final incomes = report.incomes;
    final maxLen = max(expenses.length, incomes.length);

    String dateHeaderStr;
    if (st.reportStartDate != null && st.reportEndDate != null) {
      final s = DateFormat('dd/MM/yyyy').format(st.reportStartDate!);
      final e = DateFormat('dd/MM/yyyy').format(st.reportEndDate!);
      dateHeaderStr = s == e ? 'DATE $s' : 'DATE $s - $e';
    } else if (st.reportStartDate != null) {
      dateHeaderStr = 'DATE FROM ${DateFormat('dd/MM/yyyy').format(st.reportStartDate!)}';
    } else if (st.reportEndDate != null) {
      dateHeaderStr = 'DATE UNTIL ${DateFormat('dd/MM/yyyy').format(st.reportEndDate!)}';
    } else {
      dateHeaderStr = 'DATE ${DateFormat('dd/MM/yyyy').format(DateTime.now())}';
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.black, width: 1.2),
        boxShadow: const [
          BoxShadow(color: Color(0x06000000), blurRadius: 16, offset: Offset(0, 4)),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          // Header Paper Look
          Container(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Column(
              children: [
                Text(
                  'PAPAY GARAGE',
                  style: GoogleFonts.oswald(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 2.0,
                    color: Colors.black,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  dateHeaderStr,
                  style: GoogleFonts.oswald(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.0,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, thickness: 1.2, color: Colors.black),
          // Table Layout
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: ConstrainedBox(
              constraints: const BoxConstraints(minWidth: 780),
              child: Table(
                border: TableBorder.all(color: Colors.black, width: 1.0),
                columnWidths: const {
                  0: const FixedColumnWidth(85),
                  1: const FlexColumnWidth(2.5),
                  2: const FixedColumnWidth(85),
                  3: const FlexColumnWidth(2.5),
                  4: const FixedColumnWidth(85),
                  5: const FixedColumnWidth(95),
                },
                children: [
                  // Table Header
                  TableRow(
                    decoration: const BoxDecoration(color: Color(0xFFEEEEEE)),
                    children: [
                      _thCell('Date'),
                      _thCell('Expenses Description'),
                      _thCell('QTR'),
                      _thCell('Income Description'),
                      _thCell('QTR'),
                      _thCell('Total (QTR)'),
                    ],
                  ),
                  // Table Rows
                  if (maxLen == 0)
                    TableRow(
                      children: [
                        _tdCell('-', align: TextAlign.center),
                        _tdCell('No expenses for this period', isMuted: true),
                        _tdCell('0.00', align: TextAlign.right),
                        _tdCell('No income for this period', isMuted: true),
                        _tdCell('0.00', align: TextAlign.right),
                        _tdCell('0.00', align: TextAlign.right),
                      ],
                    )
                  else
                    for (int i = 0; i < maxLen; i++) ...[
                      () {
                        final exp = i < expenses.length ? expenses[i] : null;
                        final inc = i < incomes.length ? incomes[i] : null;

                        String totalText = '';
                        Color totalColor = Colors.black87;
                        if (exp != null || inc != null) {
                          final diff = (inc?.price ?? 0.0) - (exp?.price ?? 0.0);
                          if (diff > 0) {
                            totalText = '+${diff.toStringAsFixed(2)}';
                            totalColor = const Color(0xFF1E6B37);
                          } else if (diff < 0) {
                            totalText = '-${diff.abs().toStringAsFixed(2)}';
                            totalColor = const Color(0xFFB3261E);
                          } else {
                            totalText = '0.00';
                            totalColor = Colors.black87;
                          }
                        }

                        return TableRow(
                          children: [
                            _tdCell(
                              exp != null
                                  ? DateFormat('dd/MM/yyyy').format(exp.createdAt)
                                  : (inc != null
                                      ? DateFormat('dd/MM/yyyy').format(inc.createdAt)
                                      : ''),
                              align: TextAlign.center,
                            ),
                            _tdCell(exp?.description ?? ''),
                            _tdCell(
                              exp != null ? exp.price.toStringAsFixed(2) : '',
                              align: TextAlign.right,
                            ),
                            _tdCell(inc?.description ?? ''),
                            _tdCell(
                              inc != null ? inc.price.toStringAsFixed(2) : '',
                              align: TextAlign.right,
                            ),
                            _tdCell(
                              totalText,
                              align: TextAlign.right,
                              color: totalColor,
                              fontWeight: FontWeight.w700,
                            ),
                          ],
                        );
                      }(),
                    ],
                  // Totals Row
                  TableRow(
                    decoration: const BoxDecoration(color: Color(0xFFF5F5F5)),
                    children: [
                      _thCell(''),
                      _thCell('TOTAL EXPENSES', align: TextAlign.right),
                      _thCell(report.totalExpense.toStringAsFixed(2), align: TextAlign.right),
                      _thCell('TOTAL INCOME', align: TextAlign.right),
                      _thCell(report.totalIncome.toStringAsFixed(2), align: TextAlign.right),
                      _thCell(
                        '${report.net >= 0 ? '+' : '-'}${report.net.abs().toStringAsFixed(2)}',
                        align: TextAlign.right,
                        color: report.net >= 0 ? const Color(0xFF1E6B37) : const Color(0xFFB3261E),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          // Footer Net Balance Strip
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: const BoxDecoration(
              color: Color(0xFFEEEEEE),
              border: Border(top: BorderSide(color: Colors.black, width: 1.2)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'NET BALANCE / PROFIT (صافي الأرباح):',
                  style: GoogleFonts.oswald(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                    color: Colors.black,
                  ),
                ),
                Text(
                  '${report.net >= 0 ? '+' : '-'}${report.net.abs().toStringAsFixed(2)} QTR',
                  style: GoogleFonts.oswald(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: report.net >= 0 ? const Color(0xFF1E6B37) : const Color(0xFFB3261E),
                  ),
                ),
              ],
            ),
          ),
          // Bottom Print Action Button
          Container(
            padding: const EdgeInsets.all(16),
            color: const Color(0xFFFAF8F5),
            child: Center(
              child: ElevatedButton.icon(
                onPressed: () => printInsuranceFinanceReport(
                  context,
                  report,
                  startDate: st.reportStartDate,
                  endDate: st.reportEndDate,
                ),
                icon: const Icon(Icons.print_rounded, size: 18, color: Colors.white),
                label: Text(
                  'Print Ledger Sheet',
                  style: GoogleFonts.oswald(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.8,
                    color: Colors.white,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _ink,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _thCell(String text, {TextAlign align = TextAlign.center, Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
      child: Text(
        text,
        textAlign: align,
        style: GoogleFonts.oswald(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: color ?? Colors.black,
        ),
      ),
    );
  }

  Widget _tdCell(
    String text, {
    TextAlign align = TextAlign.left,
    bool isMuted = false,
    Color? color,
    FontWeight? fontWeight,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Text(
        text,
        textAlign: align,
        style: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: fontWeight ?? FontWeight.w500,
          color: color ?? (isMuted ? _muted : Colors.black87),
        ),
      ),
    );
  }


  Widget _buildSectionBanner(String title, Color color, IconData icon) {
    final compact = _isCompact(context);
    return Container(
      padding: EdgeInsets.symmetric(horizontal: compact ? 16 : 24, vertical: 16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        border: Border(bottom: BorderSide(color: color.withValues(alpha: 0.12))),
      ),
      child: Row(
        children: [
          Icon(icon, size: 15, color: color),
          const SizedBox(width: 8),
          Text(
            title,
            style: GoogleFonts.oswald(
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.1,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDraftSection() {
    final cat = _cat;
    final rows = _draftRows[_activeId]!;
    final total = rows.fold(0.0, (s, r) => s + _rowTotal(r));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 20),
        _buildInteractiveTable(cat, rows),
        const SizedBox(height: 20),
        _buildDraftFooter(total),
      ],
    );
  }

  Widget _buildInteractiveTable(RecordCategory cat, List<Map<String, dynamic>> rows) {
    final compact = _isCompact(context);
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFFAF9F6),
        border: Border.all(color: _border),
        borderRadius: BorderRadius.circular(14),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          if (!compact) ...[
            Container(
              color: const Color(0xFFF3EFE8),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
              child: Row(
                children: [
                  SizedBox(
                    width: 32,
                    child: Text(
                      '#',
                      style: GoogleFonts.oswald(
                          fontSize: 11, fontWeight: FontWeight.w600, color: _muted),
                    ),
                  ),
                  ...cat.columns.map((c) => Expanded(
                        flex: (c.flex * 10).toInt(),
                        child: Text(
                          c.label.toUpperCase(),
                          style: GoogleFonts.oswald(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: _muted),
                        ),
                      )),
                  const SizedBox(width: 36),
                ],
              ),
            ),
            const Divider(height: 1, color: _border),
          ],
          ...rows.asMap().entries.map((e) => _TableRow(
                idx: e.key,
                row: e.value,
                cat: cat,
                accentColor: _cCol,
                canRemove: rows.length > 1,
                onRemove: () => _removeRow(e.value['id']),
                onChanged: (k, v) => _updateRow(e.value['id'], k, v),
                isLast: e.key == rows.length - 1,
              )),
        ],
      ),
    );
  }

  Widget _buildDraftFooter(double total) {
    final compact = _isCompact(context);
    final totalCol = Column(
      crossAxisAlignment:
          compact ? CrossAxisAlignment.start : CrossAxisAlignment.end,
      children: [
        Text(
          'ESTIMATED TOTAL',
          style: GoogleFonts.oswald(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.9,
              color: _muted),
        ),
        Text(
          'QR ${total.toStringAsFixed(2)}',
          style: GoogleFonts.jetBrainsMono(
              fontSize: 20, fontWeight: FontWeight.w700, color: _cCol),
        ),
      ],
    );

    final saveBtn = _SaveButton(
      color: _cCol,
      loading: context.select<InsuranceRecordsState, bool>((s) => s.isLoading),
      label: 'Save ${_cat.label}',
      expand: compact,
      onTap: _save,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        if (compact || constraints.maxWidth < 480) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _AddRowButton(color: _cCol, softColor: _sCol, onTap: _addRow),
              const SizedBox(height: 16),
              totalCol,
              const SizedBox(height: 12),
              saveBtn,
            ],
          );
        }

        return Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _AddRowButton(color: _cCol, softColor: _sCol, onTap: _addRow),
            Row(
              children: [
                totalCol,
                const SizedBox(width: 20),
                saveBtn,
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildSavedSection() {
    final st = context.watch<InsuranceRecordsState>();
    final cat = _cat;

    List<dynamic> list = [];
    switch (cat.id) {
      case 'income':
        list = st.incomes;
        break;
      case 'expense':
        list = st.expenses;
        break;
    }

    final expanded = _savedExpanded[_activeId]!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 20),
        Wrap(
          spacing: 12,
          runSpacing: 10,
          children: [
            _FetchButton(
              color: _cCol,
              loading: st.isLoading,
              onTap: st.isLoading ? null : () => _fetchCurrent(st),
            ),
            if (expanded)
              _HideButton(
                onTap: () => setState(() => _savedExpanded[_activeId] = false),
              ),
          ],
        ),
        if (expanded) ...[
          const SizedBox(height: 20),
          if (st.isLoading)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: CircularProgressIndicator(color: _cCol, strokeWidth: 2.5),
              ),
            )
          else if (list.isEmpty)
            _EmptyState(color: _cCol)
          else
            _buildSavedList(list, cat),
        ],
      ],
    );
  }

  Widget _buildSavedList(List<dynamic> list, RecordCategory cat) {
    final st = context.watch<InsuranceRecordsState>();
    final hasMore = st.hasMoreFor(cat.id);
    final loadingMore = st.isLoadingMore;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: _border),
            borderRadius: BorderRadius.circular(14),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (!_isCompact(context)) ...[
                Container(
                  color: const Color(0xFFF7F4EF),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 36,
                        child: Text(
                          '#',
                          style: GoogleFonts.oswald(
                              fontSize: 11, fontWeight: FontWeight.w600, color: _muted),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          'DESCRIPTION / INFO',
                          style: GoogleFonts.oswald(
                              fontSize: 11, fontWeight: FontWeight.w600, color: _muted),
                        ),
                      ),
                      SizedBox(
                        width: 110,
                        child: Text(
                          'PRICE',
                          textAlign: TextAlign.right,
                          style: GoogleFonts.oswald(
                              fontSize: 11, fontWeight: FontWeight.w600, color: _muted),
                        ),
                      ),
                      const SizedBox(width: 68),
                    ],
                  ),
                ),
                const Divider(height: 1, color: _border),
              ],
              ...list.asMap().entries.map((e) => _InsuranceSavedRow(
                    idx: e.key,
                    item: e.value as Map<String, dynamic>,
                    catId: cat.id,
                    accentColor: Color(cat.color),
                    onDelete: () => _delete(e.value['id']),
                    onEdit: () => _edit(e.value as Map<String, dynamic>),
                    isLast: e.key == list.length - 1,
                  )),
            ],
          ),
        ),
        if (hasMore || loadingMore) ...[
          const SizedBox(height: 14),
          Center(
            child: loadingMore
                ? Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(color: _cCol, strokeWidth: 2),
                    ),
                  )
                : TextButton.icon(
                    onPressed: () => context.read<InsuranceRecordsState>().loadMoreFor(cat.id),
                    icon: const Icon(Icons.expand_more_rounded, size: 18, color: _goldDark),
                    label: Text(
                      'Load 10 more',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: _goldDark,
                      ),
                    ),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                  ),
          ),
        ],
      ],
    );
  }
}

// ─── Table Row (Draft inputs) ────────────────────────────────────────────────
class _TableRow extends StatefulWidget {
  final int idx;
  final Map<String, dynamic> row;
  final RecordCategory cat;
  final Color accentColor;
  final bool canRemove, isLast;
  final VoidCallback onRemove;
  final void Function(String, String) onChanged;

  const _TableRow({
    required this.idx,
    required this.row,
    required this.cat,
    required this.accentColor,
    required this.canRemove,
    required this.isLast,
    required this.onRemove,
    required this.onChanged,
  });

  @override
  State<_TableRow> createState() => _TableRowState();
}

class _TableRowState extends State<_TableRow> {
  late final Map<String, TextEditingController> _controllers;

  @override
  void initState() {
    super.initState();
    _controllers = {
      for (final col in widget.cat.columns)
        col.key: TextEditingController(text: widget.row[col.key]?.toString() ?? ''),
    };
  }

  @override
  void didUpdateWidget(covariant _TableRow oldWidget) {
    super.didUpdateWidget(oldWidget);
    for (final col in widget.cat.columns) {
      final currentText = widget.row[col.key]?.toString() ?? '';
      if (_controllers[col.key]?.text != currentText) {
        _controllers[col.key]?.text = currentText;
      }
    }
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isCompact(context)) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          border: widget.isLast ? null : const Border(bottom: BorderSide(color: _border)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'ROW #${widget.idx + 1}',
                  style: GoogleFonts.oswald(
                      fontSize: 10.5,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.8,
                      color: _muted),
                ),
                if (widget.canRemove)
                  InkWell(
                    onTap: widget.onRemove,
                    borderRadius: BorderRadius.circular(6),
                    child: const Padding(
                      padding: EdgeInsets.all(4),
                      child: Icon(Icons.close_rounded, size: 16, color: Color(0xFFCC5A5A)),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            ...widget.cat.columns.map((c) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        c.label.toUpperCase(),
                        style: GoogleFonts.oswald(
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.8,
                            color: _muted),
                      ),
                      const SizedBox(height: 5),
                      _buildInput(c),
                    ],
                  ),
                )),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        border: widget.isLast ? null : const Border(bottom: BorderSide(color: _border)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 32,
            child: Text(
              '${widget.idx + 1}',
              style: GoogleFonts.jetBrainsMono(
                  fontSize: 12, color: _muted, fontWeight: FontWeight.w500),
            ),
          ),
          ...widget.cat.columns.map((c) => Expanded(
                flex: (c.flex * 10).toInt(),
                child: Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _buildInput(c),
                ),
              )),
          SizedBox(
            width: 36,
            child: widget.canRemove
                ? IconButton(
                    icon: const Icon(Icons.close_rounded, size: 16),
                    color: const Color(0xFFCC5A5A),
                    onPressed: widget.onRemove,
                    splashRadius: 16,
                  )
                : const SizedBox(),
          ),
        ],
      ),
    );
  }

  Widget _buildInput(RecordColumn col) {
    return SizedBox(
      height: 40,
      child: TextField(
        controller: _controllers[col.key],
        onChanged: (v) => widget.onChanged(col.key, v),
        keyboardType: col.type == 'number'
            ? const TextInputType.numberWithOptions(decimal: true)
            : TextInputType.text,
        style: GoogleFonts.inter(fontSize: 14, color: _ink, fontWeight: FontWeight.w500),
        decoration: InputDecoration(
          hintText: col.placeholder,
          hintStyle: GoogleFonts.inter(color: const Color(0xFFB8B0A4), fontSize: 14),
          filled: true,
          fillColor: _card,
          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
          enabledBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: _border, width: 1.5),
              borderRadius: BorderRadius.circular(8)),
          focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(color: widget.accentColor, width: 1.8),
              borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }
}

// ─── Saved Row ───────────────────────────────────────────────────────────────
class _InsuranceSavedRow extends StatefulWidget {
  final int idx;
  final Map<String, dynamic> item;
  final String catId;
  final Color accentColor;
  final VoidCallback onDelete;
  final VoidCallback onEdit;
  final bool isLast;

  const _InsuranceSavedRow({
    required this.idx,
    required this.item,
    required this.catId,
    required this.accentColor,
    required this.onDelete,
    required this.onEdit,
    required this.isLast,
  });

  @override
  State<_InsuranceSavedRow> createState() => _InsuranceSavedRowState();
}

class _InsuranceSavedRowState extends State<_InsuranceSavedRow> {
  bool _hovered = false;

  String get _title => widget.item['description'] ?? 'Unnamed Record';

  String get _dateStr {
    final raw = widget.item['created_at'];
    if (raw != null) {
      try {
        return DateFormat('MMM dd, yyyy').format(DateTime.parse(raw));
      } catch (_) {}
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final i = widget.item;
    final color = widget.accentColor;

    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 130),
        color: _hovered ? color.withValues(alpha: 0.04) : Colors.transparent,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
              child: _isCompact(context)
                  ? _buildCompactBody(i, color)
                  : _buildWideBody(i, color),
            ),
            if (!widget.isLast) const Divider(height: 1, color: _border),
          ],
        ),
      ),
    );
  }

  Widget _editButton({required double opacity}) {
    return AnimatedOpacity(
      opacity: opacity,
      duration: const Duration(milliseconds: 130),
      child: InkWell(
        onTap: widget.onEdit,
        borderRadius: BorderRadius.circular(6),
        child: const Padding(
          padding: EdgeInsets.all(5),
          child: Icon(Icons.edit_outlined, size: 17, color: _goldDark),
        ),
      ),
    );
  }

  Widget _deleteButton({required double opacity}) {
    return AnimatedOpacity(
      opacity: opacity,
      duration: const Duration(milliseconds: 130),
      child: InkWell(
        onTap: widget.onDelete,
        borderRadius: BorderRadius.circular(6),
        child: const Padding(
          padding: EdgeInsets.all(5),
          child: Icon(Icons.delete_outline_rounded, size: 17, color: Color(0xFFCC5A5A)),
        ),
      ),
    );
  }

  Widget _buildCompactBody(Map<String, dynamic> i, Color color) {
    final priceVal = double.tryParse(i['price']?.toString() ?? '0') ?? 0;
    final amountText = 'QR ${priceVal.toStringAsFixed(2)}';

    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${widget.idx + 1}.  $_title',
                style: GoogleFonts.inter(
                    fontSize: 14, fontWeight: FontWeight.w600, color: _ink),
              ),
              if (_dateStr.isNotEmpty) ...[
                const SizedBox(height: 3),
                Text(_dateStr, style: GoogleFonts.inter(fontSize: 12, color: _muted)),
              ],
              const SizedBox(height: 5),
              Text(
                amountText,
                style: GoogleFonts.jetBrainsMono(
                    fontSize: 13.5, fontWeight: FontWeight.w700, color: color),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _editButton(opacity: 1.0),
            const SizedBox(width: 4),
            _deleteButton(opacity: 1.0),
          ],
        ),
      ],
    );
  }

  Widget _buildWideBody(Map<String, dynamic> i, Color color) {
    final priceVal = double.tryParse(i['price']?.toString() ?? '0') ?? 0;
    final amountText = 'QR ${priceVal.toStringAsFixed(2)}';

    return Row(
      children: [
        SizedBox(
          width: 36,
          child: Text(
            '${widget.idx + 1}',
            style: GoogleFonts.jetBrainsMono(
                fontSize: 12, color: _muted, fontWeight: FontWeight.w500),
          ),
        ),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _title,
                style: GoogleFonts.inter(
                    fontSize: 14, fontWeight: FontWeight.w600, color: _ink),
              ),
              if (_dateStr.isNotEmpty)
                Text(_dateStr, style: GoogleFonts.inter(fontSize: 12, color: _muted)),
            ],
          ),
        ),
        SizedBox(
          width: 110,
          child: Text(
            amountText,
            textAlign: TextAlign.right,
            style: GoogleFonts.jetBrainsMono(
                fontSize: 13.5, fontWeight: FontWeight.w700, color: color),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 60,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              _editButton(opacity: _hovered ? 1.0 : 0.25),
              const SizedBox(width: 4),
              _deleteButton(opacity: _hovered ? 1.0 : 0.25),
            ],
          ),
        ),
      ],
    );
  }
}

// ─── Button Widgets ──────────────────────────────────────────────────────────
class _AddRowButton extends StatelessWidget {
  final Color color, softColor;
  final VoidCallback onTap;
  const _AddRowButton({
    required this.color,
    required this.softColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) => InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          width: _isCompact(context) ? double.infinity : null,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          decoration: BoxDecoration(
            color: softColor,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.25), width: 1.5),
          ),
          child: Row(
            mainAxisSize:
                _isCompact(context) ? MainAxisSize.max : MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.add_rounded, size: 18, color: color),
              const SizedBox(width: 6),
              Text('Add row',
                  style: GoogleFonts.inter(
                      fontSize: 14, fontWeight: FontWeight.w700, color: color)),
            ],
          ),
        ),
      );
}

class _SaveButton extends StatelessWidget {
  final Color color;
  final bool loading;
  final VoidCallback? onTap;
  final String label;
  final bool expand;

  const _SaveButton({
    required this.color,
    required this.loading,
    required this.onTap,
    required this.label,
    this.expand = false,
  });

  @override
  Widget build(BuildContext context) => SizedBox(
        width: expand ? double.infinity : null,
        child: Material(
          color: onTap == null ? color.withValues(alpha: 0.5) : color,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 15),
              child: Row(
                mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (loading)
                    const SizedBox(
                      width: 17,
                      height: 17,
                      child: CircularProgressIndicator(
                          strokeWidth: 2.2, color: Colors.white),
                    )
                  else
                    const Icon(Icons.save_rounded, size: 18, color: Colors.white),
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: GoogleFonts.inter(
                        fontSize: 14.5,
                        fontWeight: FontWeight.w700,
                        color: Colors.white),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
}

class _FetchButton extends StatelessWidget {
  final Color color;
  final bool loading;
  final VoidCallback? onTap;
  const _FetchButton({
    required this.color,
    required this.loading,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) => Material(
        color: onTap == null ? color.withValues(alpha: 0.5) : color,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 13),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (loading)
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                else
                  const Icon(Icons.refresh_rounded, size: 17, color: Colors.white),
                const SizedBox(width: 8),
                Text(
                  'Fetch Records',
                  style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: Colors.white),
                ),
              ],
            ),
          ),
        ),
      );
}

class _HideButton extends StatelessWidget {
  final VoidCallback onTap;
  const _HideButton({required this.onTap});

  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
        onPressed: onTap,
        icon: const Icon(Icons.visibility_off_outlined, size: 16, color: _muted),
        label: Text(
          'Hide',
          style: GoogleFonts.inter(
              fontSize: 13.5, fontWeight: FontWeight.w600, color: _muted),
        ),
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: _border, width: 1.5),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 13),
        ),
      );
}

class _EmptyState extends StatelessWidget {
  final Color color;
  const _EmptyState({required this.color});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(vertical: 36),
        decoration: BoxDecoration(
          color: const Color(0xFFFAF8F5),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _border),
        ),
        child: Column(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.10),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.inbox_rounded, color: color, size: 26),
            ),
            const SizedBox(height: 12),
            Text(
              'No records found',
              style: GoogleFonts.inter(
                  fontSize: 14, fontWeight: FontWeight.w600, color: _muted),
            ),
            const SizedBox(height: 4),
            Text(
              'Add rows above to create your first entry.',
              style: GoogleFonts.inter(fontSize: 12.5, color: _muted),
            ),
          ],
        ),
      );
}

class _GlassButton extends StatelessWidget {
  final VoidCallback onTap;
  final Widget child;
  const _GlassButton({required this.onTap, required this.child});

  @override
  Widget build(BuildContext context) => InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _card,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _border, width: 1.5),
          ),
          child: child,
        ),
      );
}
