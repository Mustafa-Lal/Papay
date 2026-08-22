import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../core/auth/auth_state.dart';
import 'owner_state.dart';

// ─────────────────────────────────────────────────────────────
// Design tokens
// ─────────────────────────────────────────────────────────────
const _gold     = Color(0xFFB8863A);
const _goldDark = Color(0xFF9C6F2C);
const _goldSoft = Color(0xFFF5EAD4);
const _ink      = Color(0xFF1C1812);
const _muted    = Color(0xFF9A9080);
const _border   = Color(0xFFE8E1D4);
const _bg       = Color(0xFFEEE9DF);
const _cardBg   = Color(0xFFFFFFFF);

final _fmt = NumberFormat('#,##0.00', 'en');

// ─────────────────────────────────────────────────────────────
// Responsive helpers
// ─────────────────────────────────────────────────────────────
bool _isDesktop(BuildContext context) =>
    MediaQuery.of(context).size.width >= 768;

EdgeInsets _screenPadding(BuildContext context) => _isDesktop(context)
    ? const EdgeInsets.symmetric(horizontal: 40, vertical: 32)
    : const EdgeInsets.symmetric(horizontal: 16, vertical: 20);

// ─────────────────────────────────────────────────────────────
// Screen
// ─────────────────────────────────────────────────────────────
class OwnerDashboardScreen extends StatefulWidget {
  const OwnerDashboardScreen({super.key});

  @override
  State<OwnerDashboardScreen> createState() => _OwnerDashboardScreenState();
}

class _OwnerDashboardScreenState extends State<OwnerDashboardScreen> {
  late int _year;
  late int _month;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _year  = now.year;
    _month = now.month;
    WidgetsBinding.instance.addPostFrameCallback((_) => _fetch());
  }

  void _fetch() => context.read<OwnerState>().fetchSummary(_year, _month);

  Future<void> _pickMonth() async {
    int tempYear  = _year;
    int tempMonth = _month;

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) {
          return Dialog(
            backgroundColor: _cardBg,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: SizedBox(
              width: 340,
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Select Month',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _ink)),
                    const SizedBox(height: 20),
                    const Text('Year',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: _muted)),
                    const SizedBox(height: 8),
                    Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: _border, width: 1.5),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<int>(
                          value: tempYear,
                          isExpanded: true,
                          icon: const Icon(Icons.keyboard_arrow_down, color: _muted),
                          style: const TextStyle(
                              fontSize: 15, fontWeight: FontWeight.w700, color: _ink),
                          dropdownColor: _cardBg,
                          items: List.generate(
                            11,
                            (i) => DropdownMenuItem(
                              value: 2020 + i,
                              child: Text('${2020 + i}'),
                            ),
                          ),
                          onChanged: (v) => setDlg(() => tempYear = v!),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Month',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: _muted)),
                    const SizedBox(height: 8),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 4,
                        mainAxisSpacing: 8,
                        crossAxisSpacing: 8,
                        childAspectRatio: 2,
                      ),
                      itemCount: 12,
                      itemBuilder: (_, i) {
                        final m        = i + 1;
                        final selected = m == tempMonth;
                        return GestureDetector(
                          onTap: () => setDlg(() => tempMonth = m),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 120),
                            decoration: BoxDecoration(
                              color: selected ? _gold : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                  color: selected ? _gold : _border, width: 1.5),
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              _monthAbbr(m),
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: selected ? Colors.white : _ink,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () => Navigator.pop(ctx, false),
                          child: const Text('Cancel',
                              style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed: () => Navigator.pop(ctx, true),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _gold,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10)),
                            padding: const EdgeInsets.symmetric(
                                horizontal: 22, vertical: 12),
                            textStyle: const TextStyle(
                                fontWeight: FontWeight.w700, fontSize: 14),
                          ),
                          child: const Text('Apply'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );

    if (result == true && mounted) {
      setState(() {
        _year  = tempYear;
        _month = tempMonth;
      });
      _fetch();
    }
  }

  static String _monthAbbr(int m) => const [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ][m - 1];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Padding(
          padding: _screenPadding(context),
          child: Column(
            children: [
              _buildTopBar(context),
              SizedBox(height: _isDesktop(context) ? 32 : 20),
              Expanded(child: _buildBody(context)),
            ],
          ),
        ),
      ),
    );
  }

  // ── Top bar ────────────────────────────────────────────────
  Widget _buildTopBar(BuildContext context) {
    final desktop   = _isDesktop(context);
    final monthName = DateFormat('MMMM yyyy').format(DateTime(_year, _month));

    // Shared button style factory
    ButtonStyle _outlineStyle() => OutlinedButton.styleFrom(
          foregroundColor: _ink,
          backgroundColor: _cardBg,
          side: const BorderSide(color: _border, width: 1.5),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: EdgeInsets.symmetric(
            horizontal: desktop ? 20 : 12,
            vertical: 20,
          ),
          textStyle:
              const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
        ).copyWith(
          side: WidgetStateProperty.resolveWith((s) =>
              s.contains(WidgetState.hovered)
                  ? const BorderSide(color: _goldDark, width: 1.5)
                  : const BorderSide(color: _border, width: 1.5)),
          foregroundColor: WidgetStateProperty.resolveWith((s) =>
              s.contains(WidgetState.hovered) ? _goldDark : _ink),
        );

    // Logo + title block
    final titleBlock = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: desktop ? 56 : 44,
          height: desktop ? 56 : 44,
          decoration: BoxDecoration(
            color: _goldSoft,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(Icons.bar_chart_rounded,
              color: _gold, size: desktop ? 28 : 22),
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Owner Dashboard',
              style: TextStyle(
                fontSize: desktop ? 28 : 20,
                fontWeight: FontWeight.w800,
                color: _ink,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Summary for $monthName',
              style: TextStyle(
                fontSize: desktop ? 15 : 12,
                color: _muted,
              ),
            ),
          ],
        ),
      ],
    );

    // Action buttons — full labels on desktop, icon-only on mobile
    final actions = desktop
        ? Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              OutlinedButton.icon(
                onPressed: _pickMonth,
                icon: const Icon(Icons.calendar_month_outlined, size: 16),
                label: Text(monthName),
                style: _outlineStyle(),
              ),
              const SizedBox(width: 12),
              OutlinedButton.icon(
                onPressed: _fetch,
                icon: const Icon(Icons.refresh, size: 16),
                label: const Text('Refresh'),
                style: _outlineStyle(),
              ),
              const SizedBox(width: 12),
              OutlinedButton.icon(
                onPressed: () => context.read<AuthState>().logout(),
                icon: const Icon(Icons.logout, size: 16),
                label: const Text('Log out'),
                style: _outlineStyle(),
              ),
            ],
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Tooltip(
                message: monthName,
                child: OutlinedButton(
                  onPressed: _pickMonth,
                  style: _outlineStyle(),
                  child: const Icon(Icons.calendar_month_outlined, size: 18),
                ),
              ),
              const SizedBox(width: 8),
              Tooltip(
                message: 'Refresh',
                child: OutlinedButton(
                  onPressed: _fetch,
                  style: _outlineStyle(),
                  child: const Icon(Icons.refresh, size: 18),
                ),
              ),
              const SizedBox(width: 8),
              Tooltip(
                message: 'Log out',
                child: OutlinedButton(
                  onPressed: () => context.read<AuthState>().logout(),
                  style: _outlineStyle(),
                  child: const Icon(Icons.logout, size: 18),
                ),
              ),
            ],
          );

    // Desktop: single Row; Mobile: Column
    if (desktop) {
      return Row(
        children: [
          Expanded(child: titleBlock),
          actions,
        ],
      );
    } else {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          titleBlock,
          const SizedBox(height: 14),
          actions,
        ],
      );
    }
  }

  // ── Body ───────────────────────────────────────────────────
  Widget _buildBody(BuildContext context) {
    return Consumer<OwnerState>(
      builder: (context, state, _) {
        if (state.loading) {
          return const Center(
              child: CircularProgressIndicator(color: _gold));
        }
        if (state.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 40, color: Colors.red),
                const SizedBox(height: 12),
                Text(state.error!,
                    style: const TextStyle(color: _muted)),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _fetch,
                  style: ElevatedButton.styleFrom(backgroundColor: _gold),
                  child: const Text('Retry',
                      style: TextStyle(color: Colors.white)),
                ),
              ],
            ),
          );
        }
        if (state.summary == null) {
          return const Center(
              child: Text('No data yet.',
                  style: TextStyle(color: _muted)));
        }

        final s = state.summary!;
        return SingleChildScrollView(
          child: Column(
            children: [
              _NetBar(summary: s),
              const SizedBox(height: 24),
              _ProfitColumn(summary: s),
              const SizedBox(height: 16),
              _ExpenseColumn(summary: s),
              const SizedBox(height: 32),
            ],
          ),
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────
// Net Summary Bar
// ─────────────────────────────────────────────────────────────
class _NetBar extends StatelessWidget {
  final MonthlySummary summary;
  const _NetBar({required this.summary});

  @override
  Widget build(BuildContext context) {
    final desktop    = _isDesktop(context);
    final isPositive = summary.net >= 0;

    // Shared items
    final profitItem  = _NetItem(label: 'Total Profit',  value: summary.totalProfit,  light: true);
    final expenseItem = _NetItem(label: 'Total Expense', value: summary.totalExpense, light: true);
    final netItem     = Column(
      children: [
        Text('Net',
            style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: desktop ? 12 : 11,
                fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        Text(
          'QAR ${_fmt.format(summary.net)}',
          style: TextStyle(
            color: Colors.white,
            fontSize: desktop ? 22 : 18,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          padding:
              const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            isPositive ? '▲ Surplus' : '▼ Deficit',
            style: const TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700),
          ),
        ),
      ],
    );

    final dividerV = Container(
        width: 1, height: 48, color: Colors.white.withValues(alpha: 0.3));
    final dividerH = Divider(
        color: Colors.white.withValues(alpha: 0.3), height: 28);

    return Container(
      padding: EdgeInsets.all(desktop ? 28 : 20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_gold, _goldDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
              color: _gold.withValues(alpha: 0.25),
              blurRadius: 24,
              offset: const Offset(0, 8))
        ],
      ),
      // On desktop: horizontal row; on mobile: vertical column
      child: desktop
          ? Row(
              children: [
                Expanded(child: profitItem),
                dividerV,
                Expanded(child: expenseItem),
                dividerV,
                Expanded(child: netItem),
              ],
            )
          : Column(
              children: [
                profitItem,
                dividerH,
                expenseItem,
                dividerH,
                netItem,
              ],
            ),
    );
  }
}

class _NetItem extends StatelessWidget {
  final String label;
  final double value;
  final bool light;
  const _NetItem(
      {required this.label, required this.value, this.light = false});

  @override
  Widget build(BuildContext context) {
    final desktop = _isDesktop(context);
    final color   = light ? Colors.white : _ink;
    final mColor  = light ? Colors.white.withValues(alpha: 0.7) : _muted;
    return Column(
      children: [
        Text(label,
            style: TextStyle(
                color: mColor,
                fontSize: desktop ? 12 : 11,
                fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        Text(
          'QAR ${_fmt.format(value)}',
          style: TextStyle(
              color: color,
              fontSize: desktop ? 18 : 15,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────
// Profit Column
// ─────────────────────────────────────────────────────────────
class _ProfitColumn extends StatelessWidget {
  final MonthlySummary summary;
  const _ProfitColumn({required this.summary});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _SectionCard(
          icon: Icons.shield_outlined,
          title: 'Insurance Profit',
          child: _ProfitBreakdownRow(breakdown: summary.insuranceProfit),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.build_outlined,
          title: 'Mechanic Profit',
          subtitle: 'Labor charges + commissions only',
          child: _ProfitBreakdownRow(breakdown: summary.mechanicProfit),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.inventory_2_outlined,
          title: 'Parts Profit',
          subtitle: 'Garage records — profits table',
          child: _AmountRow(
              label: 'Total', amount: summary.partsProfit, highlight: true),
        ),
      ],
    );
  }
}

class _ProfitBreakdownRow extends StatelessWidget {
  final InvoiceProfitBreakdown breakdown;
  const _ProfitBreakdownRow({required this.breakdown});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _AmountRow(label: 'Total', amount: breakdown.total, highlight: true),
        const SizedBox(height: 10),
        // Badges: wrap on mobile so they don't get squished
        _isDesktop(context)
            ? Row(children: [
                Expanded(
                    child: _BadgeAmount(
                        label: 'Paid',
                        amount: breakdown.paid,
                        color: const Color(0xFF2DAA62))),
                const SizedBox(width: 10),
                Expanded(
                    child: _BadgeAmount(
                        label: 'Unpaid',
                        amount: breakdown.unpaid,
                        color: const Color(0xFFE04340))),
              ])
            : Column(children: [
                _BadgeAmount(
                    label: 'Paid',
                    amount: breakdown.paid,
                    color: const Color(0xFF2DAA62)),
                const SizedBox(height: 8),
                _BadgeAmount(
                    label: 'Unpaid',
                    amount: breakdown.unpaid,
                    color: const Color(0xFFE04340)),
              ]),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────
// Expense Column
// ─────────────────────────────────────────────────────────────
class _ExpenseColumn extends StatelessWidget {
  final MonthlySummary summary;
  const _ExpenseColumn({required this.summary});

  @override
  Widget build(BuildContext context) {
    final util = summary.utilityExpense;
    final sal  = summary.salaryExpense;

    return Column(
      children: [
        _SectionCard(
          icon: Icons.receipt_long_outlined,
          title: 'Product Expense',
          child: _AmountRow(label: 'Total', amount: summary.productExpense),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.home_work_outlined,
          title: 'Rent Expense',
          child: _AmountRow(label: 'This month', amount: summary.rentExpense),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.bolt_outlined,
          title: 'Utility Expense',
          child: Column(
            children: [
              _AmountRow(label: 'Internet',     amount: util.internet),
              const SizedBox(height: 8),
              _AmountRow(label: 'Electricity',  amount: util.electricity),
              const SizedBox(height: 8),
              _AmountRow(label: 'Water',        amount: util.water),
              const Divider(color: _border, height: 20),
              _AmountRow(label: 'Total', amount: util.total, highlight: true),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.people_outline,
          title: 'Salary Expense',
          child: Column(
            children: [
              if (sal.employees.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8),
                  child: Text('No salaries recorded',
                      style: TextStyle(color: _muted, fontSize: 13)),
                )
              else
                ...sal.employees.map((e) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: _AmountRow(label: e.name, amount: e.amount),
                    )),
              const Divider(color: _border, height: 20),
              _AmountRow(label: 'Total', amount: sal.total, highlight: true),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _SectionCard(
          icon: Icons.store_outlined,
          title: 'Garage Expense',
          subtitle: 'Garage records — expenses table',
          child: _AmountRow(label: 'Total', amount: summary.garageExpense),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────
// Shared UI components
// ─────────────────────────────────────────────────────────────
class _SectionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget child;

  const _SectionCard({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final desktop = _isDesktop(context);
    return Container(
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _border),
        boxShadow: const [
          BoxShadow(
              color: Color(0x05211D16), blurRadius: 24, offset: Offset(0, 8))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: EdgeInsets.fromLTRB(
                desktop ? 20 : 14, 18, desktop ? 20 : 14, 14),
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                      color: _goldSoft,
                      borderRadius: BorderRadius.circular(9)),
                  child: Icon(icon, size: 18, color: _goldDark),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: TextStyle(
                              fontSize: desktop ? 15 : 14,
                              fontWeight: FontWeight.w800,
                              color: _ink)),
                      if (subtitle != null)
                        Text(subtitle!,
                            style: TextStyle(
                                fontSize: desktop ? 11.5 : 11,
                                color: _muted)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: _border, height: 1),
          Padding(
            padding: EdgeInsets.symmetric(
              horizontal: desktop ? 32 : 16,
              vertical: desktop ? 24 : 16,
            ),
            child: child,
          ),
        ],
      ),
    );
  }
}

class _AmountRow extends StatelessWidget {
  final String label;
  final double amount;
  final bool highlight;

  const _AmountRow(
      {required this.label, required this.amount, this.highlight = false});

  @override
  Widget build(BuildContext context) {
    final desktop = _isDesktop(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Flexible(
          child: Text(
            label,
            style: TextStyle(
              fontSize: desktop ? 13.5 : 13,
              fontWeight: highlight ? FontWeight.w700 : FontWeight.w500,
              color: highlight ? _ink : _muted,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          'QAR ${_fmt.format(amount)}',
          style: TextStyle(
            fontSize: highlight
                ? (desktop ? 16 : 14)
                : (desktop ? 14 : 13),
            fontWeight:
                highlight ? FontWeight.w800 : FontWeight.w600,
            color: highlight ? _gold : _ink,
          ),
        ),
      ],
    );
  }
}

class _BadgeAmount extends StatelessWidget {
  final String label;
  final double amount;
  final Color color;

  const _BadgeAmount(
      {required this.label, required this.amount, required this.color});

  @override
  Widget build(BuildContext context) {
    final desktop = _isDesktop(context);
    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(
          horizontal: desktop ? 12 : 10, vertical: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label,
              style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: color)),
          const SizedBox(height: 4),
          Text(
            'QAR ${_fmt.format(amount)}',
            style: TextStyle(
                fontSize: desktop ? 14 : 13,
                fontWeight: FontWeight.w800,
                color: color),
          ),
        ],
      ),
    );
  }
}