import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/record_models.dart';
import '../providers/records_state.dart';
import 'dart:math';

// ─── Design Tokens ───────────────────────────────────────────────────────────
// Typography system:
//   • Oswald          — headers, section banners, uppercase eyebrow labels, tab labels
//   • Inter            — body copy, input text, buttons, dialogs
//   • JetBrains Mono    — money, quantities, dates — anything numeric/tabular
const _ink = Color(0xFF1C1812);
const _muted = Color(0xFF9A9080);
const _border = Color(0xFFE8E1D4);
const _bg = Color(0xFFEEE9DF);
const _card = Color(0xFFFFFFFF);
const _inputBg = Color(0xFFFCFBF8);

// Unified golden accent — replaces the old per-category colors so every tab
// (Products, Rent, Salary, Utility, Profit, Expense) shares one identity,
// matching the activation screen's gold key icon and CTA button.
const _gold = Color(0xFFB8863A); // primary accent — buttons, active states, totals
const _goldDark = Color(0xFF9A6E28); // darker text on tinted surfaces
const _goldTint = Color(0xFFF3E2B8); // tab bar track background
const _goldSoft = Color(0xFFFBF2DD); // soft fills: banners, add-row button, chips

const _compactBreakpoint = 840.0;
bool _isCompact(BuildContext context) => MediaQuery.sizeOf(context).width < _compactBreakpoint;

// ─── Category Definitions ────────────────────────────────────────────────────
// Every category now shares the same gold + goldTint pair instead of a unique
// hue, so the whole screen reads as one consistent, on-brand tool.
final _categories = [
  RecordCategory(
    id: 'products', label: 'Products', icon: 'package',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'description', label: 'Product Name', type: 'text', flex: 2.0, placeholder: 'e.g. Brake Shoe'),
      RecordColumn(key: 'quantity',    label: 'Qty',          type: 'number', flex: 1.0, placeholder: '1'),
      RecordColumn(key: 'unit_price',  label: 'Price (QR)',   type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
  RecordCategory(
    id: 'rent', label: 'Rent', icon: 'home',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'amount', label: 'Amount (QR)', type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
  RecordCategory(
    id: 'salary', label: 'Salary', icon: 'users',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'name',   label: 'Employee Name', type: 'text',   flex: 2.0, placeholder: 'e.g. Ahmed Khan'),
      RecordColumn(key: 'amount', label: 'Amount (QR)',   type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
  RecordCategory(
    id: 'utility', label: 'Utility Bills', icon: 'zap',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'bill_type', label: 'Bill Type',   type: 'select', flex: 1.4, placeholder: 'Select...', options: ['ELECTRICITY', 'WATER', 'INTERNET']),
      RecordColumn(key: 'amount',    label: 'Amount (QR)', type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
  RecordCategory(
    id: 'profit', label: 'Profit', icon: 'trending-up',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'name',   label: 'Source / Name', type: 'text',   flex: 2.0, placeholder: 'e.g. Extra service income'),
      RecordColumn(key: 'amount', label: 'Amount (QR)',   type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
  RecordCategory(
    id: 'expense', label: 'Expense', icon: 'trending-down',
    color: 0xFFB8863A, softColor: 0xFFF3E2B8,
    columns: [
      RecordColumn(key: 'description', label: 'Description', type: 'text',   flex: 2.0, placeholder: 'e.g. Office supplies'),
      RecordColumn(key: 'amount',       label: 'Amount (QR)', type: 'number', flex: 1.0, placeholder: '0.00'),
    ],
  ),
];

Map<String, dynamic> _emptyRow(RecordCategory cat) {
  final row = <String, dynamic>{
    'id': '${DateTime.now().millisecondsSinceEpoch}${Random().nextInt(9999)}',
  };
  for (final c in cat.columns) {
    row[c.key] = c.type == 'select' ? (c.options?.first ?? '') : '';
  }
  return row;
}

double _rowTotal(RecordCategory cat, Map<String, dynamic> row) {
  if (cat.id == 'products') {
    final qty   = double.tryParse(row['quantity']?.toString()  ?? '0') ?? 0;
    final price = double.tryParse(row['unit_price']?.toString() ?? '0') ?? 0;
    return qty * price;
  }
  return double.tryParse(row['amount']?.toString() ?? '0') ?? 0;
}

// ─── Screen ──────────────────────────────────────────────────────────────────
class GarageRecordsScreen extends StatefulWidget {
  const GarageRecordsScreen({super.key});
  @override
  State<GarageRecordsScreen> createState() => _GarageRecordsScreenState();
}

class _GarageRecordsScreenState extends State<GarageRecordsScreen>
    with TickerProviderStateMixin {
  String _activeId = 'products';

  final Map<String, DateTime>                    _draftDates    = {};
  final Map<String, List<Map<String, dynamic>>>  _draftRows     = {};
  final Map<String, bool>                        _savedExpanded = {};

  late AnimationController _tabAnimCtrl;
  late Animation<double>   _tabAnim;

  @override
  void initState() {
    super.initState();
    for (final cat in _categories) {
      _draftDates[cat.id]    = DateTime.now();
      _draftRows[cat.id]     = [_emptyRow(cat)];
      _savedExpanded[cat.id] = false;
    }
    _tabAnimCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 220));
    _tabAnim     = CurvedAnimation(parent: _tabAnimCtrl, curve: Curves.easeOut);
    _tabAnimCtrl.forward();
  }

  @override
  void dispose() {
    _tabAnimCtrl.dispose();
    super.dispose();
  }

  RecordCategory get _cat  => _categories.firstWhere((c) => c.id == _activeId);
  Color          get _cCol => Color(_cat.color);
  Color          get _sCol => Color(_cat.softColor);

  void _switchTab(String id) {
    if (id == _activeId) return;
    setState(() => _activeId = id);
    _tabAnimCtrl
      ..reset()
      ..forward();
  }

  void _updateRow(String rowId, String key, String val) {
    setState(() {
      final rows = _draftRows[_activeId]!;
      final idx  = rows.indexWhere((r) => r['id'] == rowId);
      if (idx != -1) rows[idx][key] = val;
    });
  }

  void _addRow()             => setState(() => _draftRows[_activeId]!.add(_emptyRow(_cat)));
  void _removeRow(String id) => setState(() {
    final rows = _draftRows[_activeId]!;
    rows.removeWhere((r) => r['id'] == id);
    if (rows.isEmpty) rows.add(_emptyRow(_cat));
  });

  Future<void> _save() async {
    final st   = context.read<RecordsState>();
    final cat  = _cat;
    final rows = List<Map<String, dynamic>>.from(_draftRows[_activeId]!);
    final date = _draftDates[_activeId]!;

    if (cat.id == 'products') {
      for (final row in rows) {
        final desc = row['description']?.toString().trim() ?? '';
        final priceStr = row['unit_price']?.toString().trim() ?? '';
        
        if (desc.isEmpty) {
          _showToast('Product name/description is required.', success: false);
          return;
        }
        
        if (priceStr.isEmpty || double.tryParse(priceStr) == null || double.parse(priceStr) < 0) {
          _showToast('A valid product price is required.', success: false);
          return;
        }
      }
    }
    
    if (cat.id == 'rent') {
      for (final row in rows) {
        final amountStr = row['amount']?.toString().trim() ?? '';
        if (amountStr.isEmpty || double.tryParse(amountStr) == null || double.parse(amountStr) < 0) {
          _showToast('A valid rent amount is required.', success: false);
          return;
        }
      }
    }

    if (cat.id == 'salary') {
      for (final row in rows) {
        final name = row['name']?.toString().trim() ?? '';
        final amountStr = row['amount']?.toString().trim() ?? '';
        
        if (name.isEmpty) {
          _showToast('Employee name is required.', success: false);
          return;
        }
        
        if (amountStr.isEmpty || double.tryParse(amountStr) == null || double.parse(amountStr) < 0) {
          _showToast('A valid salary amount is required.', success: false);
          return;
        }
      }
    }

    if (cat.id == 'utility') {
      for (final row in rows) {
        final amountStr = row['amount']?.toString().trim() ?? '';
        if (amountStr.isEmpty || double.tryParse(amountStr) == null || double.parse(amountStr) < 0) {
          _showToast('A valid utility bill amount is required.', success: false);
          return;
        }
      }
    }

    if (cat.id == 'profit') {
      for (final row in rows) {
        final name = row['name']?.toString().trim() ?? '';
        final amountStr = row['amount']?.toString().trim() ?? '';
        if (name.isEmpty) {
          _showToast('Profit source/name is required.', success: false);
          return;
        }
        if (amountStr.isEmpty || double.tryParse(amountStr) == null || double.parse(amountStr) < 0) {
          _showToast('A valid profit amount is required.', success: false);
          return;
        }
      }
    }

    if (cat.id == 'expense') {
      for (final row in rows) {
        final desc = row['description']?.toString().trim() ?? '';
        final amountStr = row['amount']?.toString().trim() ?? '';
        if (desc.isEmpty) {
          _showToast('Expense description is required.', success: false);
          return;
        }
        if (amountStr.isEmpty || double.tryParse(amountStr) == null || double.parse(amountStr) < 0) {
          _showToast('A valid expense amount is required.', success: false);
          return;
        }
      }
    }

    bool ok = false;
    switch (cat.id) {
      case 'products': ok = await st.saveProducts(rows);           break;
      case 'rent':     ok = await st.saveRents(rows, date);        break;
      case 'salary':   ok = await st.saveSalaries(rows);           break;
      case 'utility':  ok = await st.saveUtilityBills(rows, date); break;
      case 'profit':   ok = await st.saveProfits(rows);            break;
      case 'expense':  ok = await st.saveExpenses(rows);           break;
    }

    if (!mounted) return;
    if (ok) {
      _showToast('${cat.label} saved!', success: true);
      setState(() {
        _draftRows[_activeId]  = [_emptyRow(cat)];
        _draftDates[_activeId] = DateTime.now();
      });
    } else {
      _showToast(st.errorMessage ?? 'Error saving records', success: false);
    }
  }

  Future<void> _delete(int id) async {
    final confirmed = await _showDeleteDialog();
    if (!confirmed || !mounted) return;
    final st = context.read<RecordsState>();
    switch (_activeId) {
      case 'products': st.deleteProduct(id);     break;
      case 'rent':     st.deleteRent(id);        break;
      case 'salary':   st.deleteSalary(id);      break;
      case 'utility':  st.deleteUtilityBill(id); break;
      case 'profit':   st.deleteProfit(id);      break;
      case 'expense':  st.deleteExpense(id);     break;
    }
  }

  Future<bool> _showDeleteDialog() async {
    return await showDialog<bool>(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Container(
          width: 360,
          constraints: BoxConstraints(maxWidth: MediaQuery.sizeOf(ctx).width - 40),
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 44, height: 44,
                decoration: BoxDecoration(color: const Color(0xFFFDE8E8), borderRadius: BorderRadius.circular(12)),
                child: const Icon(Icons.delete_outline_rounded, color: Color(0xFFC24C4A), size: 22),
              ),
              const SizedBox(height: 16),
              Text('Delete Record', style: GoogleFonts.oswald(fontSize: 18, fontWeight: FontWeight.w600, color: _ink, letterSpacing: 0.2)),
              const SizedBox(height: 8),
              Text('This action cannot be undone.', style: GoogleFonts.inter(fontSize: 14, color: _muted, height: 1.5)),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: _border, width: 1.5),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        foregroundColor: _ink,
                      ),
                      child: Text('Cancel', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
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
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        padding: const EdgeInsets.symmetric(vertical: 13),
                      ),
                      child: Text('Delete', style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    ) ?? false;
  }

  void _showToast(String msg, {required bool success}) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Row(children: [
        Icon(success ? Icons.check_circle_rounded : Icons.error_rounded, color: Colors.white, size: 18),
        const SizedBox(width: 10),
        Expanded(child: Text(msg, style: GoogleFonts.inter(fontWeight: FontWeight.w600, color: Colors.white))),
      ]),
      backgroundColor: success ? const Color(0xFF4A8F6A) : const Color(0xFFC24C4A),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(16),
      duration: const Duration(seconds: 3),
    ));
  }

  void _fetchCurrent(RecordsState st) {
    setState(() => _savedExpanded[_activeId] = true);
    switch (_activeId) {
      case 'products': st.fetchProducts(); break;
      case 'rent':     st.fetchRents();    break;
      case 'salary':   st.setMonthYearForSalaries(DateTime.now().year, DateTime.now().month); break;
      case 'utility':  st.setMonthYearForUtility(DateTime.now().year, DateTime.now().month);  break;
      case 'profit':   st.fetchProfits();  break;
      case 'expense':  st.fetchExpenses(); break;
    }
  }

  IconData _icon(String name) {
    switch (name) {
      case 'package':       return Icons.inventory_2_rounded;
      case 'home':          return Icons.home_work_rounded;
      case 'users':         return Icons.group_rounded;
      case 'zap':           return Icons.bolt_rounded;
      case 'trending-up':   return Icons.trending_up_rounded;
      case 'trending-down': return Icons.trending_down_rounded;
      default:              return Icons.circle;
    }
  }

  @override
  Widget build(BuildContext context) {
    final compact = _isCompact(context);
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: SingleChildScrollView(
        padding: EdgeInsets.symmetric(horizontal: compact ? 16 : 44, vertical: compact ? 20 : 36),
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
                position: Tween<Offset>(begin: const Offset(0, 0.04), end: Offset.zero).animate(_tabAnim),
                child: _buildMainCard(),
              ),
            ),
            const SizedBox(height: 40),
          ],
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
              Text('Garage Records', style: GoogleFonts.oswald(fontSize: compact ? 22 : 26, fontWeight: FontWeight.w600, color: _ink, letterSpacing: 0.2)),
              const SizedBox(height: 3),
              Text('Track products, rent, salaries, utilities, profits & expenses', style: GoogleFonts.inter(fontSize: compact ? 12.5 : 13.5, color: _muted)),
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
      final cColor   = Color(cat.color);
      return GestureDetector(
        onTap: () => _switchTab(cat.id),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
          margin: const EdgeInsets.symmetric(horizontal: 3),
          padding: EdgeInsets.symmetric(vertical: 11, horizontal: compact ? 10 : 0),
          decoration: BoxDecoration(
            color: isActive ? _card : Colors.transparent,
            borderRadius: BorderRadius.circular(11),
            boxShadow: isActive
                ? [BoxShadow(color: cColor.withValues(alpha: 0.18), blurRadius: 12, offset: const Offset(0, 4))]
                : [],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(_icon(cat.icon), size: 18, color: isActive ? cColor : _muted),
              const SizedBox(height: 5),
              Text(
                cat.label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.oswald(
                  fontSize: 11.5,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
                  letterSpacing: 0.3,
                  color: isActive ? cColor : _muted,
                ),
                textAlign: TextAlign.center,
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
      child: compact
          ? SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: _categories.map((cat) => SizedBox(width: 104, child: tab(cat))).toList(),
              ),
            )
          : Row(
              children: _categories.map((cat) => Expanded(child: tab(cat))).toList(),
            ),
    );
  }

  Widget _buildMainCard() {
    final pad = _isCompact(context) ? 16.0 : 24.0;
    return Container(
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border),
        boxShadow: const [BoxShadow(color: Color(0x0A000000), blurRadius: 32, offset: Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSectionBanner('ADD NEW ${_cat.label.toUpperCase()}', _cCol, Icons.add_circle_outline_rounded),
          Padding(padding: EdgeInsets.fromLTRB(pad, 0, pad, pad), child: _buildDraftSection()),
          const Divider(height: 1, color: _border),
          _buildSectionBanner('SAVED ${_cat.label.toUpperCase()}', _cCol, Icons.history_rounded),
          Padding(padding: EdgeInsets.fromLTRB(pad, 0, pad, pad), child: _buildSavedSection()),
        ],
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
          Text(title, style: GoogleFonts.oswald(fontSize: 11.5, fontWeight: FontWeight.w600, letterSpacing: 1.1, color: color)),
        ],
      ),
    );
  }

  Widget _buildDraftSection() {
    final cat   = _cat;
    final rows  = _draftRows[_activeId]!;
    final total = rows.fold(0.0, (s, r) => s + _rowTotal(cat, r));
    final needDate = cat.id == 'rent' || cat.id == 'utility';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 20),
        if (needDate) ...[
          Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 12,
            runSpacing: 8,
            children: [
              Text('PERIOD', style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w500, letterSpacing: 1.0, color: _muted)),
              _DateChip(
                date: _draftDates[_activeId]!,
                color: _cCol,
                onTap: () async {
                  final d = await showDatePicker(
                    context: context,
                    initialDate: _draftDates[_activeId]!,
                    firstDate: DateTime(2000),
                    lastDate: DateTime(2100),
                  );
                  if (d != null) setState(() => _draftDates[_activeId] = d);
                },
              ),
            ],
          ),
          const SizedBox(height: 20),
        ],

        if (!_isCompact(context)) ...[
          _TableHeader(cat: cat),
          const SizedBox(height: 4),
        ],

        ...rows.asMap().entries.map((e) => _DraftRow(
          key: ValueKey(e.value['id']),
          idx: e.key,
          row: e.value,
          cat: cat,
          accentColor: _cCol,
          onChanged: (k, v) => _updateRow(e.value['id'], k, v),
          onRemove: () => _removeRow(e.value['id']),
        )),

        const SizedBox(height: 12),
        _buildDraftActions(cat, total),
      ],
    );
  }

  Widget _buildDraftActions(RecordCategory cat, double total) {
    final compact = _isCompact(context);
    final saving = context.select<RecordsState, bool>((s) => s.isLoading);
    final saveBtn = saving
        ? _SaveButton(color: _cCol, loading: true, onTap: null, label: 'Saving...', expand: compact)
        : _SaveButton(color: _cCol, loading: false, onTap: _save, label: 'Save ${cat.label}', expand: compact);
    final totalCol = Column(
      crossAxisAlignment: compact ? CrossAxisAlignment.start : CrossAxisAlignment.end,
      children: [
        Text('BATCH TOTAL', style: GoogleFonts.oswald(fontSize: 10.5, fontWeight: FontWeight.w500, letterSpacing: 1.0, color: _muted)),
        Text('QR ${total.toStringAsFixed(2)}', style: GoogleFonts.jetBrainsMono(fontSize: compact ? 18 : 20, fontWeight: FontWeight.w700, color: _cCol)),
      ],
    );

    if (compact) {
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
  }

  Widget _buildSavedSection() {
    final st   = context.watch<RecordsState>();
    final cat  = _cat;

    List<dynamic> list = [];
    switch (cat.id) {
      case 'products': list = st.products;     break;
      case 'rent':     list = st.rents;        break;
      case 'salary':   list = st.salaries;     break;
      case 'utility':  list = st.utilityBills; break;
      case 'profit':   list = st.profits;      break;
      case 'expense':  list = st.expenses;     break;
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
            if (expanded) _HideButton(onTap: () => setState(() => _savedExpanded[_activeId] = false)),
          ],
        ),
        if (expanded) ...[
          const SizedBox(height: 20),
          if (st.isLoading)
            Center(child: Padding(
              padding: const EdgeInsets.all(32),
              child: CircularProgressIndicator(color: _cCol, strokeWidth: 2.5),
            ))
          else if (list.isEmpty)
            _EmptyState(color: _cCol)
          else
            _buildSavedList(list, cat),
        ],
      ],
    );
  }

  Widget _buildSavedList(List<dynamic> list, RecordCategory cat) {
    final isProducts = cat.id == 'products';
    final st = context.watch<RecordsState>();
    final hasMore = st.hasMoreFor(cat.id);
    final loadingMore = st.isLoadingMore;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          decoration: BoxDecoration(border: Border.all(color: _border), borderRadius: BorderRadius.circular(14)),
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
                      SizedBox(width: 36, child: Text('#', style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                      if (isProducts) ...[
                        Expanded(flex: 20, child: Text('PRODUCT', style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                        SizedBox(width: 80, child: Text('QTY', textAlign: TextAlign.center, style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                        SizedBox(width: 100, child: Text('UNIT PRICE', textAlign: TextAlign.right, style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                        SizedBox(width: 100, child: Text('TOTAL', textAlign: TextAlign.right, style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                      ] else ...[
                        Expanded(child: Text('NAME / INFO', style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                        SizedBox(width: 110, child: Text('AMOUNT', textAlign: TextAlign.right, style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
                      ],
                      const SizedBox(width: 36),
                    ],
                  ),
                ),
                const Divider(height: 1, color: _border),
              ],
              ...list.asMap().entries.map((e) => _SavedRow(
                idx: e.key,
                item: e.value as Map<String, dynamic>,
                catId: cat.id,
                accentColor: Color(cat.color),
                isProducts: isProducts,
                onDelete: () => _delete(e.value['id']),
                isLast: e.key == list.length - 1,
              )),
            ],
          ),
        ),

        // Load More button
        if (hasMore || loadingMore) ...[
          const SizedBox(height: 12),
          Center(
            child: loadingMore
                ? Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(color: _cCol, strokeWidth: 2),
                    ),
                  )
                : TextButton.icon(
                    onPressed: () => context.read<RecordsState>().loadMoreFor(cat.id),
                    icon: Icon(Icons.expand_more_rounded, size: 18, color: _goldDark),
                    label: Text(
                      'Load 10 more',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: _goldDark,
                      ),
                    ),
                    style: TextButton.styleFrom(
                      backgroundColor: _goldSoft,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
          ),
        ],
      ],
    );
  }
}

// ─── Reusable Sub-Widgets ─────────────────────────────────────────────────────

class _GlassButton extends StatelessWidget {
  final VoidCallback onTap;
  final Widget child;
  const _GlassButton({required this.onTap, required this.child});

  @override
  Widget build(BuildContext context) => Material(
    color: _card,
    borderRadius: BorderRadius.circular(12),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 44, height: 44,
        decoration: BoxDecoration(border: Border.all(color: _border, width: 1.5), borderRadius: BorderRadius.circular(12)),
        child: Center(child: child),
      ),
    ),
  );
}

class _DateChip extends StatelessWidget {
  final DateTime date;
  final Color color;
  final VoidCallback onTap;
  const _DateChip({required this.date, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(10),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        border: Border.all(color: color.withValues(alpha: 0.3), width: 1.5),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.calendar_month_rounded, size: 15, color: color),
          const SizedBox(width: 8),
          Text(DateFormat('MMMM yyyy').format(date), style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w700, color: color)),
          const SizedBox(width: 8),
          Icon(Icons.keyboard_arrow_down_rounded, size: 16, color: color.withValues(alpha: 0.7)),
        ],
      ),
    ),
  );
}

class _TableHeader extends StatelessWidget {
  final RecordCategory cat;
  const _TableHeader({required this.cat});

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
    decoration: BoxDecoration(color: const Color(0xFFF7F4EF), borderRadius: BorderRadius.circular(10)),
    child: Row(
      children: [
        SizedBox(width: 36, child: Text('#', style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
        ...cat.columns.map((c) => Expanded(
          flex: (c.flex * 10).toInt(),
          child: Text(c.label.toUpperCase(), style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted)),
        )),
        SizedBox(width: 110, child: Text('AMOUNT', textAlign: TextAlign.right, style: GoogleFonts.oswald(fontSize: 11, fontWeight: FontWeight.w600, color: _muted))),
        const SizedBox(width: 36),
      ],
    ),
  );
}

class _DraftRow extends StatelessWidget {
  final int idx;
  final Map<String, dynamic> row;
  final RecordCategory cat;
  final Color accentColor;
  final Function(String key, String val) onChanged;
  final VoidCallback onRemove;
  const _DraftRow({super.key, required this.idx, required this.row, required this.cat, required this.accentColor, required this.onChanged, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    final total = _rowTotal(cat, row);
    if (_isCompact(context)) {
      return Container(
        margin: const EdgeInsets.only(top: 10),
        padding: const EdgeInsets.fromLTRB(14, 12, 10, 14),
        decoration: BoxDecoration(
          color: _inputBg,
          border: Border.all(color: _border, width: 1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Text('${idx + 1}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: _muted)),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.remove_circle_outline_rounded, size: 20),
                  color: const Color(0xFFCC5A5A),
                  onPressed: onRemove,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  splashRadius: 18,
                ),
              ],
            ),
            const SizedBox(height: 4),
            ...cat.columns.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(c.label.toUpperCase(), style: GoogleFonts.oswald(fontSize: 10.5, fontWeight: FontWeight.w600, letterSpacing: 0.8, color: _muted)),
                  const SizedBox(height: 6),
                  _buildField(c),
                ],
              ),
            )),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                total > 0 ? 'QR ${total.toStringAsFixed(2)}' : '—',
                style: GoogleFonts.jetBrainsMono(fontSize: 15, fontWeight: FontWeight.w700, color: total > 0 ? accentColor : _muted),
              ),
            ),
          ],
        ),
      );
    }
    return Container(
      margin: const EdgeInsets.only(top: 6),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: _inputBg,
        border: Border.all(color: _border, width: 1),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(width: 36, child: Text('${idx + 1}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: _muted))),
          ...cat.columns.map((c) => Expanded(
            flex: (c.flex * 10).toInt(),
            child: Padding(padding: const EdgeInsets.only(right: 10), child: _buildField(c)),
          )),
          SizedBox(
            width: 110,
            child: Text(
              total > 0 ? 'QR ${total.toStringAsFixed(2)}' : '—',
              textAlign: TextAlign.right,
              style: GoogleFonts.jetBrainsMono(fontSize: 14, fontWeight: FontWeight.w700, color: total > 0 ? accentColor : _muted),
            ),
          ),
          const SizedBox(width: 4),
          SizedBox(
            width: 32,
            child: IconButton(
              icon: const Icon(Icons.remove_circle_outline_rounded, size: 18),
              color: const Color(0xFFCC5A5A),
              onPressed: onRemove,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
              splashRadius: 18,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildField(RecordColumn col) {
    if (col.type == 'select') {
      final val = row[col.key]?.toString() ?? '';
      return Container(
        height: 40,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        decoration: BoxDecoration(
          color: _card,
          border: Border.all(color: _border, width: 1.5),
          borderRadius: BorderRadius.circular(8),
        ),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<String>(
            value: val.isEmpty ? null : val,
            hint: Text(col.placeholder, style: GoogleFonts.inter(color: const Color(0xFFB4AB9A), fontSize: 14)),
            isExpanded: true,
            icon: const Icon(Icons.unfold_more_rounded, color: _muted, size: 16),
            dropdownColor: _card,
            style: GoogleFonts.inter(color: _ink, fontSize: 14, fontWeight: FontWeight.w600),
            items: col.options?.map((o) => DropdownMenuItem(value: o, child: Text(o))).toList(),
            onChanged: (v) { if (v != null) onChanged(col.key, v); },
          ),
        ),
      );
    }
    return SizedBox(
      height: 40,
      child: TextField(
        controller: TextEditingController.fromValue(
          TextEditingValue(text: row[col.key]?.toString() ?? '', selection: TextSelection.collapsed(offset: (row[col.key]?.toString() ?? '').length)),
        ),
        onChanged: (v) => onChanged(col.key, v),
        keyboardType: col.type == 'number' ? const TextInputType.numberWithOptions(decimal: true) : TextInputType.text,
        style: GoogleFonts.inter(fontSize: 14, color: _ink, fontWeight: FontWeight.w500),
        decoration: InputDecoration(
          hintText: col.placeholder,
          hintStyle: GoogleFonts.inter(color: const Color(0xFFB8B0A4), fontSize: 14),
          filled: true,
          fillColor: _card,
          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
          enabledBorder: OutlineInputBorder(borderSide: const BorderSide(color: _border, width: 1.5), borderRadius: BorderRadius.circular(8)),
          focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: accentColor, width: 1.8), borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }
}

class _AddRowButton extends StatelessWidget {
  final Color color, softColor;
  final VoidCallback onTap;
  const _AddRowButton({required this.color, required this.softColor, required this.onTap});

  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(10),
    child: Container(
      width: _isCompact(context) ? double.infinity : null,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: softColor,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.25), width: 1.5),
      ),
      child: Row(
        mainAxisSize: _isCompact(context) ? MainAxisSize.max : MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
        Icon(Icons.add_rounded, size: 17, color: color),
        const SizedBox(width: 6),
        Text('Add row', style: GoogleFonts.inter(fontSize: 13.5, fontWeight: FontWeight.w700, color: color)),
      ]),
    ),
  );
}

class _SaveButton extends StatelessWidget {
  final Color color;
  final bool loading;
  final VoidCallback? onTap;
  final String label;
  final bool expand;
  const _SaveButton({required this.color, required this.loading, required this.onTap, required this.label, this.expand = false});

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
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 13),
        child: Row(
          mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
          if (loading)
            const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
          else
            const Icon(Icons.save_rounded, size: 17, color: Colors.white),
          const SizedBox(width: 8),
          Text(label, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w700, color: Colors.white)),
        ]),
      ),
    ),
  ),
  );
}

class _FetchButton extends StatelessWidget {
  final Color color;
  final bool loading;
  final VoidCallback? onTap;
  const _FetchButton({required this.color, required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) => Material(
    color: onTap == null ? color.withValues(alpha: 0.5) : color,
    borderRadius: BorderRadius.circular(10),
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          if (loading)
            const SizedBox(width: 15, height: 15, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
          else
            const Icon(Icons.download_rounded, size: 16, color: Colors.white),
          const SizedBox(width: 8),
          Text('Fetch Records', style: GoogleFonts.inter(fontSize: 13.5, fontWeight: FontWeight.w700, color: Colors.white)),
        ]),
      ),
    ),
  );
}

class _HideButton extends StatelessWidget {
  final VoidCallback onTap;
  const _HideButton({required this.onTap});

  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(10),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
      decoration: BoxDecoration(border: Border.all(color: _border, width: 1.5), borderRadius: BorderRadius.circular(10)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.visibility_off_outlined, size: 15, color: _muted),
        const SizedBox(width: 6),
        Text('Hide', style: GoogleFonts.inter(fontSize: 13.5, fontWeight: FontWeight.w600, color: _muted)),
      ]),
    ),
  );
}

class _EmptyState extends StatelessWidget {
  final Color color;
  const _EmptyState({required this.color});

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(vertical: 40),
    decoration: BoxDecoration(border: Border.all(color: _border), borderRadius: BorderRadius.circular(14)),
    child: Column(children: [
      Icon(Icons.inbox_rounded, size: 36, color: color.withValues(alpha: 0.3)),
      const SizedBox(height: 10),
      Text('No records found', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: _muted)),
      const SizedBox(height: 4),
      Text('Add entries above and save them', style: GoogleFonts.inter(fontSize: 12.5, color: _muted)),
    ]),
  );
}

class _SavedRow extends StatefulWidget {
  final int idx;
  final Map<String, dynamic> item;
  final String catId;
  final Color accentColor;
  final bool isProducts;
  final VoidCallback onDelete;
  final bool isLast;
  const _SavedRow({required this.idx, required this.item, required this.catId, required this.accentColor, required this.isProducts, required this.onDelete, required this.isLast});

  @override
  State<_SavedRow> createState() => _SavedRowState();
}

class _SavedRowState extends State<_SavedRow> {
  bool _hovered = false;

  String get _title {
    switch (widget.catId) {
      case 'products': return widget.item['description'] ?? 'Unnamed Product';
      case 'rent':     return 'Rent Payment';
      case 'salary':   return widget.item['name'] ?? 'Unnamed Employee';
      case 'utility':  return widget.item['bill_type'] ?? 'Utility Bill';
      case 'profit':   return widget.item['name'] ?? 'Profit';
      case 'expense':  return widget.item['description'] ?? 'Expense';
      default:         return 'Record';
    }
  }

  String get _subtitle {
    final c = widget.catId;
    final i = widget.item;
    if (c == 'products') return 'Qty: ${i['quantity']}';
    if (c == 'rent' || c == 'utility') {
      final m = int.tryParse(i['month']?.toString() ?? '1') ?? 1;
      return '${i['year']} · ${DateFormat('MMMM').format(DateTime(2000, m))}';
    }
    if (i['created_at'] != null) {
      try { return DateFormat('MMM dd, yyyy').format(DateTime.parse(i['created_at'])); }
      catch (_) {}
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final i     = widget.item;
    final color = widget.accentColor;

    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit:  (_) => setState(() => _hovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 130),
        color: _hovered ? color.withValues(alpha: 0.04) : Colors.transparent,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
              child: _isCompact(context) ? _buildCompactBody(i, color) : _buildWideBody(i, color),
            ),
            if (!widget.isLast) const Divider(height: 1, color: _border),
          ],
        ),
      ),
    );
  }

  Widget _deleteButton({required double opacity}) {
    return AnimatedOpacity(
      opacity: opacity,
      duration: const Duration(milliseconds: 130),
      child: IconButton(
        icon: const Icon(Icons.delete_outline_rounded, size: 17),
        color: const Color(0xFFCC5A5A),
        onPressed: widget.onDelete,
        padding: EdgeInsets.zero,
        constraints: const BoxConstraints(),
        splashRadius: 18,
      ),
    );
  }

  Widget _buildCompactBody(Map<String, dynamic> i, Color color) {
    String amountText;
    String? extra;
    if (widget.isProducts) {
      extra = 'Qty ${i['quantity'] ?? '—'}  ·  QR ${i['unit_price'] ?? '—'}';
      final qty   = double.tryParse(i['quantity']?.toString()   ?? '0') ?? 0;
      final price = double.tryParse(i['unit_price']?.toString() ?? '0') ?? 0;
      amountText = 'QR ${(qty * price).toStringAsFixed(2)}';
    } else {
      extra = _subtitle.isNotEmpty ? _subtitle : null;
      amountText = 'QR ${double.tryParse(i['amount']?.toString() ?? '0')?.toStringAsFixed(2) ?? '—'}';
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('${widget.idx + 1}.  $_title', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: _ink)),
              if (extra != null && extra.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(extra, style: GoogleFonts.jetBrainsMono(fontSize: 12, color: _muted)),
              ],
              const SizedBox(height: 6),
              Text(amountText, style: GoogleFonts.jetBrainsMono(fontSize: 14.5, fontWeight: FontWeight.w700, color: color)),
            ],
          ),
        ),
        _deleteButton(opacity: 1),
      ],
    );
  }

  Widget _buildWideBody(Map<String, dynamic> i, Color color) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        SizedBox(width: 36, child: Text('${widget.idx + 1}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: _muted))),
        if (widget.isProducts) ...[
          Expanded(flex: 20, child: Text(_title, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: _ink))),
          SizedBox(width: 80, child: Text('${i['quantity'] ?? '—'}', textAlign: TextAlign.center, style: GoogleFonts.jetBrainsMono(fontSize: 14, color: _muted, fontWeight: FontWeight.w500))),
          SizedBox(width: 100, child: Text('QR ${i['unit_price'] ?? '—'}', textAlign: TextAlign.right, style: GoogleFonts.jetBrainsMono(fontSize: 14, color: _muted, fontWeight: FontWeight.w500))),
          SizedBox(width: 100, child: Builder(builder: (_) {
            final qty   = double.tryParse(i['quantity']?.toString()   ?? '0') ?? 0;
            final price = double.tryParse(i['unit_price']?.toString() ?? '0') ?? 0;
            return Text('QR ${(qty * price).toStringAsFixed(2)}', textAlign: TextAlign.right, style: GoogleFonts.jetBrainsMono(fontSize: 14, fontWeight: FontWeight.w700, color: color));
          })),
        ] else ...[
          Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_title, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: _ink)),
              if (_subtitle.isNotEmpty) ...[
                const SizedBox(height: 2),
                Text(_subtitle, style: GoogleFonts.jetBrainsMono(fontSize: 12, color: _muted)),
              ],
            ],
          )),
          SizedBox(
            width: 110,
            child: Text(
              'QR ${double.tryParse(i['amount']?.toString() ?? '0')?.toStringAsFixed(2) ?? '—'}',
              textAlign: TextAlign.right,
              style: GoogleFonts.jetBrainsMono(fontSize: 14.5, fontWeight: FontWeight.w700, color: color),
            ),
          ),
        ],
        const SizedBox(width: 4),
        SizedBox(width: 32, child: _deleteButton(opacity: _hovered ? 1.0 : 0.4)),
      ],
    );
  }
}