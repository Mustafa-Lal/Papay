import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/auth/auth_state.dart';
import '../models/insurance_models.dart';
import 'create_invoice_screen.dart';
import 'invoice_detail_screen.dart';
import '../../../core/widgets/plate_search_bar.dart';
import 'package:google_fonts/google_fonts.dart';

// ──────────────────────────────────────────────
// Design tokens — mirrors the "Mechanic Workspace" mockup palette
// ──────────────────────────────────────────────
const _ink = Color(0xFF1C1812);
const _bg = Color(0xFFEEE9DF);
const _surface = Color(0xFFFFFFFF);
const _surface2 = Color(0xFFFBF7EE);
const _border = Color(0xFFE8E1D4);
const _muted = Color(0xFF9A9080);
const _muted2 = Color(0xFFB5AC98);

const _accent = Color(0xFFB8863A);
const _accentDark = Color(0xFF9C6F2C);
const _accentTint = Color(0xFFF5EAD4);

const _steel = Color(0xFF7A561F);
const _steelTint = Color(0xFFFBF2DD);

const _unpaid = Color(0xFFC1443A);
const _unpaidBg = Color(0xFFFBEAE8);
const _paid = Color(0xFF2E8B57);
const _paidBg = Color(0xFFE7F5EC);

const double _radius = 10;
const double _cardPadding = 24;

// ──────────────────────────────────────────────
// Responsive tokens
// ──────────────────────────────────────────────
const double _mobileBreakpoint = 800.0;
const double _cardPaddingMobile = 16;



class InsuranceDashboardScreen extends StatefulWidget {
  const InsuranceDashboardScreen({super.key});

  @override
  State<InsuranceDashboardScreen> createState() => _InsuranceDashboardScreenState();
}

class _InsuranceDashboardScreenState extends State<InsuranceDashboardScreen> {
  final _plateController = TextEditingController();
  DateTimeRange? _selectedDateRange;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<InsuranceState>().fetchInvoices();
    });
  }

  @override
  void dispose() {
    _plateController.dispose();
    super.dispose();
  }

  void _search() {
    String? startStr;
    String? endStr;
    if (_selectedDateRange != null) {
      startStr = DateFormat('yyyy-MM-dd').format(_selectedDateRange!.start);
      endStr = DateFormat('yyyy-MM-dd').format(_selectedDateRange!.end);
    }
    context.read<InsuranceState>().setFilters(
      plate: _plateController.text.trim(),
      startDate: startStr,
      endDate: endStr,
    );
  }

  void _clearSearch() {
    _plateController.clear();
    setState(() => _selectedDateRange = null);
    context.read<InsuranceState>().setFilters(plate: null, startDate: null, endDate: null);
  }

  Future<void> _pickDateRange() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
      initialDateRange: _selectedDateRange,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: _accent,
              onPrimary: Colors.white,
              onSurface: Colors.black87,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() => _selectedDateRange = picked);
      _search();
    }
  }

  Future<void> _goToCreate() async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const CreateInvoiceScreen()),
    );
  }

  void _goToDetail(InsuranceInvoiceSummary summary) async {
    final changed = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => InvoiceDetailScreen(invoiceId: summary.invoiceId),
      ),
    );
    if (mounted && changed == true) {
      context.read<InsuranceState>().fetchInvoices();
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < _mobileBreakpoint;

    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.symmetric(
            horizontal: isMobile ? 12 : 24,
            vertical: isMobile ? 16 : 32,
          ),
          child: Column(
            children: [
              _buildTopbar(isMobile),
              const SizedBox(height: 14),
              const SizedBox(height: 14),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: _surface,
                    borderRadius: BorderRadius.circular(_radius),
                    boxShadow: const [
                      BoxShadow(color: Color(0x0A1C1B1A), blurRadius: 4, offset: Offset(0, 1)),
                      BoxShadow(color: Color(0x1A1C1B1A), blurRadius: 24, offset: Offset(0, 8)),
                    ],
                  ),
                  child: Column(
                    children: [
                      Padding(
                        padding: EdgeInsets.all(isMobile ? _cardPaddingMobile : _cardPadding),
                        child: _buildCardHeader(isMobile),
                      ),
                      const Divider(height: 1, color: _border),
                      Expanded(child: _buildList(isMobile)),
                      const Divider(height: 1, color: _border),
                      _buildFooter(isMobile),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Dark rounded topbar with the orange brand-icon block, matching the
  // mockup's `.topbar` / `.brand` / `.brand-icon`.
  Widget _buildTopbar(bool isMobile) {
    final brandRow = Row(
      children: [
        Container(
          width: isMobile ? 40 : 52,
          height: isMobile ? 40 : 52,
          decoration: BoxDecoration(
            color: _accent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(Icons.shield_outlined, color: Colors.white, size: isMobile ? 20 : 26),
        ),
        SizedBox(width: isMobile ? 12 : 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'INSURANCE WORKSPACE',
                style: GoogleFonts.oswald(
                    fontSize: isMobile ? 16 : 24, color: _accentDark, fontWeight: FontWeight.w900),
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 2),
              Text(
                'Manage and track all insurance invoices',
                style: const TextStyle(fontSize: 13.5, color: Color(0xFF9CA3AF)),
                maxLines: isMobile ? 2 : 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );

    final logoutButton = _topbarGhostButton(
      icon: Icons.logout,
      label: 'Log out',
      onPressed: () => context.read<AuthState>().logout(),
      isMobile: isMobile,
    );

    return Container(
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 16 : 28, vertical: isMobile ? 16 : 22),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(_radius),
        boxShadow: const [
          BoxShadow(color: Color(0x0A1C1B1A), blurRadius: 4, offset: Offset(0, 1)),
          BoxShadow(color: Color(0x1A1C1B1A), blurRadius: 24, offset: Offset(0, 8)),
        ],
      ),
      child: isMobile
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                brandRow,
                const SizedBox(height: 14),
                SizedBox(width: double.infinity, child: logoutButton),
              ],
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(child: brandRow),
                logoutButton,
              ],
            ),
    );
  }

  Widget _topbarGhostButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    bool isMobile = false,
  }) {
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16, color: _accent),
      label: Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: _accent)),
      style: OutlinedButton.styleFrom(
        foregroundColor: const Color(0xFFE5E7EB),
        backgroundColor: _accent,
        side: const BorderSide(color: _accentDark),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: isMobile ? 14 : 20),
        textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      ).copyWith(
        backgroundColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.hovered)) return const Color(0xFF2A2A28);
          return const Color.fromARGB(93, 184, 134, 58);
        }),
      ),
    );
  }

  Widget _buildCardHeader(bool isMobile) {
    final titleBlock = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'INVOICES',
          style: GoogleFonts.oswald(fontSize: isMobile ? 17 : 20, color: _ink, fontWeight: FontWeight.w600, letterSpacing: 0.3),
        ),
        const SizedBox(height: 4),
        const Text(
          'View, edit and manage all insurance records',
          style: TextStyle(fontSize: 14, color: _muted),
        ),
      ],
    );

    final durationButton = SizedBox(
      height: 45,
      width: isMobile ? double.infinity : null,
      child: OutlinedButton.icon(
        onPressed: _pickDateRange,
        icon: const Icon(Icons.calendar_today_outlined, size: 16, color: _accent),
        label: Text(_selectedDateRange == null
            ? 'Duration'
            : '${DateFormat('MMM d').format(_selectedDateRange!.start)} - ${DateFormat('MMM d').format(_selectedDateRange!.end)}', style: const TextStyle(color: _accent)),
        style: OutlinedButton.styleFrom(
          foregroundColor: _ink,
          backgroundColor: const Color.fromARGB(93, 184, 134, 58),
          side: const BorderSide(color: _accent),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ).copyWith(
          side: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.hovered)) return const BorderSide(color: _muted2);
            return const BorderSide(color: _accent);
          }),
        ),
      ),
    );

    final newInvoiceButton = SizedBox(
      height: 45,
      width: isMobile ? double.infinity : null,
      child: ElevatedButton.icon(
        onPressed: _goToCreate,
        icon: const Icon(Icons.add, size: 18),
        label: const Text('New Invoice'),
        style: ElevatedButton.styleFrom(
          foregroundColor: Colors.white,
          backgroundColor: _accent,
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ).copyWith(
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.hovered)) return _accentDark;
            return _accent;
          }),
        ),
      ),
    );

    if (isMobile) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          titleBlock,
          const SizedBox(height: 16),
          LayoutBuilder(
            builder: (context, constraints) => _buildSearchBar(constraints.maxWidth),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(child: durationButton),
              if (_selectedDateRange != null) ...[
                const SizedBox(width: 6),
                IconButton(
                  icon: const Icon(Icons.clear, color: _muted),
                  onPressed: _clearSearch,
                ),
              ],
            ],
          ),
          const SizedBox(height: 10),
          newInvoiceButton,
        ],
      );
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(child: titleBlock),
        const SizedBox(width: 20),
        _buildSearchBar(220),
        const SizedBox(width: 10),
        durationButton,
        if (_selectedDateRange != null) ...[
          const SizedBox(width: 6),
          IconButton(
            icon: const Icon(Icons.clear, color: _muted),
            onPressed: _clearSearch,
          ),
        ],
        const SizedBox(width: 10),
        newInvoiceButton,
      ],
    );
  }

  Widget _buildSearchBar(double width) {
    return PlateSearchBar(
      controller: _plateController,
      width: width,
      onSubmitted: (_) => _search(),
    );
  }

  Widget _buildFooter(bool isMobile) {
    return Consumer<InsuranceState>(
      builder: (context, state, _) {
        if (state.invoices.isEmpty) return const SizedBox.shrink();
        final count = state.invoices.length;
        return Padding(
          padding: EdgeInsets.symmetric(
            horizontal: isMobile ? _cardPaddingMobile : _cardPadding,
            vertical: 14,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Showing $count ${count == 1 ? 'invoice' : 'invoices'}',
                style: const TextStyle(fontSize: 13, color: _muted),
              ),
              Row(
                children: [
                  _pageButton(Icons.chevron_left, enabled: state.canGoPrev, onTap: state.previousPage),
                  const SizedBox(width: 8),
                  _pageButton(Icons.chevron_right, enabled: state.canGoNext, onTap: state.nextPage),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _pageButton(IconData icon, {required bool enabled, VoidCallback? onTap}) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(
          color: _surface,
          border: Border.all(color: _border),
          borderRadius: BorderRadius.circular(7),
        ),
        child: Icon(icon, size: 16, color: enabled ? _ink : _muted2.withValues(alpha: 0.5)),
      ),
    );
  }

  Widget _buildList(bool isMobile) {
    return Consumer<InsuranceState>(
      builder: (context, state, _) {
        if (state.isLoading && state.invoices.isEmpty) {
          return const Center(child: CircularProgressIndicator(color: _accent));
        }

        if (state.invoices.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.inbox_outlined, size: 38, color: _muted2),
                const SizedBox(height: 12),
                const Text(
                  'No invoices yet. Create one to get started.',
                  style: TextStyle(color: _muted, fontSize: 15),
                ),
              ],
            ),
          );
        }

        if (isMobile) {
          return ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: _cardPaddingMobile, vertical: 12),
            itemCount: state.invoices.length,
            itemBuilder: (context, i) => _buildMobileInvoiceCard(state.invoices[i]),
          );
        }

        return Theme(
          data: Theme.of(context).copyWith(
            dividerColor: _border,
            dataTableTheme: DataTableThemeData(
              headingRowColor: WidgetStateProperty.all(_surface2),
              dataRowColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) return const Color(0xFFFAFAF9);
                return Colors.transparent;
              }),
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: _cardPadding),
            child: SingleChildScrollView(
              child: SizedBox(
                width: double.infinity,
                child: DataTable(
                  columnSpacing: 24,
                  horizontalMargin: 0,
                  dataRowMinHeight: 60,
                  dataRowMaxHeight: 68,
                  headingRowHeight: 44,
                  headingTextStyle: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: _muted,
                    letterSpacing: 1.2,
                  ),
                  columns: const [
                    DataColumn(label: Text('CUSTOMER')),
                    DataColumn(label: Text('PLATE')),
                    DataColumn(label: Text('STATUS')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Expanded(child: Align(alignment: Alignment.centerRight, child: Text('ACTIONS')))),
                  ],
                  rows: state.invoices.map((inv) {
                    final statusColor = _statusColor(inv.paymentStatus);
                    return DataRow(
                      cells: [
                        DataCell(_buildCustomerCell(inv, statusColor)),
                        DataCell(_buildPlateBadge(inv.plateNumber)),
                        DataCell(_buildBadge(inv.paymentStatus)),
                        DataCell(Text(
                          DateFormat('MMM dd, yyyy').format(inv.invoiceDate),
                          style: GoogleFonts.jetBrainsMono(fontSize: 13, color: _ink),
                        )),
                        DataCell(Align(
                          alignment: Alignment.centerRight,
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              _buildActionButton(
                                icon: Icons.visibility_outlined,
                                label: 'View',
                                textColor: _steel,
                                bgColor: _steelTint,
                                hoverColor: const Color(0xFFDCE9F2),
                                onTap: () => _goToDetail(inv),
                              ),
                              const SizedBox(width: 6),
                              _buildActionButton(
                                icon: Icons.delete_outline,
                                label: 'Delete',
                                textColor: _unpaid,
                                bgColor: _unpaidBg,
                                hoverColor: const Color(0xFFF6D9D9),
                                onTap: () => _confirmDelete(inv),
                              ),
                            ],
                          ),
                        )),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  // Mobile-only card representation of an invoice row — a table doesn't
  // reflow well on narrow screens, so this mirrors the same data/actions
  // as the DataTable row in a stacked, touch-friendly layout.
  Widget _buildMobileInvoiceCard(InsuranceInvoiceSummary inv) {
    final statusColor = _statusColor(inv.paymentStatus);
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _surface,
        border: Border.all(color: _border),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 4, height: 32, color: statusColor),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  inv.name ?? '—',
                  style: const TextStyle(fontWeight: FontWeight.w600, color: _ink, fontSize: 14.5),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              _buildPlateBadge(inv.plateNumber),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildBadge(inv.paymentStatus),
              const Spacer(),
              Text(
                DateFormat('MMM dd, yyyy').format(inv.invoiceDate),
                style: GoogleFonts.jetBrainsMono(fontSize: 13, color: _ink),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildActionButton(
                  icon: Icons.visibility_outlined,
                  label: 'View',
                  textColor: _steel,
                  bgColor: _steelTint,
                  hoverColor: const Color(0xFFDCE9F2),
                  onTap: () => _goToDetail(inv),
                  center: true,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildActionButton(
                  icon: Icons.delete_outline,
                  label: 'Delete',
                  textColor: _unpaid,
                  bgColor: _unpaidBg,
                  hoverColor: const Color(0xFFF6D9D9),
                  onTap: () => _confirmDelete(inv),
                  center: true,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Mimics the mockup's `.tag-bar` — a thin colored strip on the leading
  // edge of the row, plus the customer name / sub-label stack.
  Widget _buildCustomerCell(InsuranceInvoiceSummary inv, Color statusColor) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 4, height: 32, color: statusColor),
        const SizedBox(width: 14),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              inv.name ?? '—',
              style: const TextStyle(fontWeight: FontWeight.w600, color: _ink, fontSize: 14.5),
            ),
          ],
        ),
      ],
    );
  }

  // Mimics the mockup's `.plate` chip — bordered, monospace, letter-spaced.
  Widget _buildPlateBadge(String plate) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFFDFDFB),
        border: Border.all(color: _ink, width: 1.5),
        borderRadius: BorderRadius.circular(5),
      ),
      child: Text(
        plate,
        style: GoogleFonts.jetBrainsMono(
          fontWeight: FontWeight.w700,
          fontSize: 13,
          letterSpacing: 1,
          color: _ink,
        ),
      ),
    );
  }

  Color _statusColor(PaymentStatus status) {
    switch (status) {
      case PaymentStatus.paid:
        return _paid;
      case PaymentStatus.partiallyPaid:
        return _accent;
      default:
        return _unpaid;
    }
  }

  Widget _buildBadge(PaymentStatus status) {
    final isPaid = status == PaymentStatus.paid;
    final isPartial = status == PaymentStatus.partiallyPaid;

    final bg = isPaid ? _paidBg : isPartial ? _accentTint : _unpaidBg;
    final fg = isPaid ? _paid : isPartial ? _accentDark : _unpaid;
    final lbl = isPaid ? 'Paid' : isPartial ? 'Partial' : 'Unpaid';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 5),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(5)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 6, height: 6, decoration: BoxDecoration(color: fg, shape: BoxShape.circle)),
          const SizedBox(width: 6),
          Text(lbl, style: TextStyle(color: fg, fontSize: 12.5, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color textColor,
    required Color bgColor,
    required Color hoverColor,
    required VoidCallback onTap,
    bool center = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(7),
      hoverColor: hoverColor,
      child: Container(
        width: center ? double.infinity : null,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(7),
        ),
        child: Row(
          mainAxisSize: center ? MainAxisSize.max : MainAxisSize.min,
          mainAxisAlignment: center ? MainAxisAlignment.center : MainAxisAlignment.start,
          children: [
            Icon(icon, size: 14, color: textColor),
            const SizedBox(width: 5),
            Text(label, style: TextStyle(color: textColor, fontSize: 13, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  Future<void> _confirmDelete(InsuranceInvoiceSummary inv) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        final dialogWidth = MediaQuery.of(ctx).size.width;
        final isMobileDialog = dialogWidth < _mobileBreakpoint;
        return Dialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          insetPadding: EdgeInsets.symmetric(
            horizontal: isMobileDialog ? 20 : (dialogWidth - 380) / 2,
            vertical: 24,
          ),
          child: Container(
            width: isMobileDialog ? double.infinity : 380,
            padding: const EdgeInsets.all(28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(color: _unpaidBg, borderRadius: BorderRadius.circular(10)),
                  child: const Icon(Icons.delete_outline_rounded, color: _unpaid, size: 22),
                ),
                const SizedBox(height: 16),
                const Text('Delete Invoice', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: _ink)),
                const SizedBox(height: 8),
                Text(
                  'Delete invoice #${inv.invoiceId} for ${inv.name ?? "this customer"}? This cannot be undone.',
                  style: const TextStyle(fontSize: 14, color: _muted, height: 1.5),
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: _border),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(vertical: 13),
                          foregroundColor: _ink,
                        ),
                        child: const Text('Cancel', style: TextStyle(fontWeight: FontWeight.w600)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () => Navigator.pop(ctx, true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _unpaid,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(vertical: 13),
                        ),
                        child: const Text('Delete', style: TextStyle(fontWeight: FontWeight.w700)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
    if (ok == true && mounted) {
      context.read<InsuranceState>().deleteInvoice(inv.invoiceId);
    }
  }
}