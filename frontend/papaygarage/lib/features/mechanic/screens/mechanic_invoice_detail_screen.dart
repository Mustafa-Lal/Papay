import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/mechanic_models.dart';
import '../providers/mechanic_state.dart';
import '../utils/mechanic_invoice_printer.dart';
import 'edit_invoice_screen.dart';
export '../providers/mechanic_state.dart';

// Design Constants
const _gold = Color(0xFFB8863A);
const _goldDark = Color(0xFF9C6F2C);
const _goldSoft = Color(0xFFF5EAD4);
const _ink = Color(0xFF1C1812);
const _muted = Color(0xFF9A9080);
const _border = Color(0xFFE8E1D4);
const _bg = Color(0xFFEEE9DF);
const _cardBg = Color(0xFFFFFFFF);
const _cardRadius = 16.0;
const _cardShadow = BoxShadow(
  color: Color(0x05211D16),
  blurRadius: 24,
  offset: Offset(0, 8),
);

class MechanicInvoiceDetailScreen extends StatefulWidget {
  final int invoiceId;
  const MechanicInvoiceDetailScreen({super.key, required this.invoiceId});

  @override
  State<MechanicInvoiceDetailScreen> createState() => _MechanicInvoiceDetailScreenState();
}

class _MechanicInvoiceDetailScreenState extends State<MechanicInvoiceDetailScreen> {
  MechanicInvoice? _invoice;
  bool _loading = true;
  String? _error;
  bool _hasChanges = false; // tracks if the dashboard list needs a refresh

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    final state = context.read<MechanicState>();
    final inv = await context.read<MechanicState>().getInvoice(widget.invoiceId);
    if (mounted) {
      setState(() {
        _invoice = inv;
        _loading = false;
        _error = inv == null ? state.errorMessage ?? 'Failed to load.' : null;
      });
    }
  }

  Future<void> _markAsPaid() async {
    if (_invoice == null) return;
    
    // Optimistic UI Update: Instantly reflect the change in the UI without waiting for the network
    setState(() {
      _invoice = _invoice!.copyWith(paymentStatus: PaymentStatus.paid);
      _hasChanges = true; // signal the dashboard to refresh its list
    });

    final state = context.read<MechanicState>();
    await state.updateInvoice(_invoice!.id, {'payment_status': 'PAID'});
    // We intentionally do not call _load() here to avoid unnecessary GET requests.
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _gold))
          : _error != null
              ? Center(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _load,
                      style: ElevatedButton.styleFrom(backgroundColor: _gold),
                      child: const Text('Retry', style: TextStyle(color: Colors.white)),
                    ),
                  ],
                ))
              : _buildBody(),
    );
  }

  Widget _buildBody() {
    final inv = _invoice!;
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildHeader(inv),
          const SizedBox(height: 32),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: _InvoiceDetailsCard(invoice: inv)),
                      const SizedBox(width: 24),
                      Expanded(child: _CustomerCard(invoice: inv, onRefresh: _load)),
                    ],
                  ),
                  const SizedBox(height: 24),
                  _RepairItemsCard(invoice: inv),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(MechanicInvoice inv) {
    final isPaid = inv.paymentStatus == PaymentStatus.paid;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                OutlinedButton(
                  onPressed: () => Navigator.pop(context, _hasChanges),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.all(20),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    side: const BorderSide(color: _border, width: 1.5),
                    backgroundColor: _cardBg,
                    foregroundColor: _ink,
                  ),
                  child: const Icon(Icons.arrow_back, size: 20, color: _ink),
                ),
                const SizedBox(width: 16),
                Text(
                  'Invoice #${inv.id}',
                  style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: _ink, letterSpacing: -0.5),
                ),
                const SizedBox(width: 16),
                _buildBadge(inv.paymentStatus),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'Generated on ${DateFormat('MMMM dd, yyyy').format(inv.invoiceDate)}',
              style: const TextStyle(fontSize: 15, color: _muted),
            ),
          ],
        ),
        Row(
          children: [
            OutlinedButton.icon(
              onPressed: () {
                if (_invoice != null) {
                  printMechanicInvoice(context, _invoice!);
                }
              },
              icon: const Icon(Icons.print_outlined, size: 16),
              label: const Text('Print'),
              style: OutlinedButton.styleFrom(
                foregroundColor: _ink,
                backgroundColor: _cardBg,
                side: const BorderSide(color: _border, width: 1.5),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13.5),
              ),
            ),
            const SizedBox(width: 12),
            OutlinedButton.icon(
              onPressed: () async {
                if (_invoice == null) return;
                final changed = await Navigator.push<bool>(
                  context,
                  MaterialPageRoute(
                    builder: (_) => EditInvoiceScreen(invoice: _invoice!),
                  ),
                );
                if (mounted && changed == true) {
                  setState(() { _hasChanges = true; });
                  _load();
                }
              },
              icon: const Icon(Icons.edit_outlined, size: 16),
              label: const Text('Edit'),
              style: OutlinedButton.styleFrom(
                foregroundColor: _ink,
                backgroundColor: _cardBg,
                side: const BorderSide(color: _border, width: 1.5),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13.5),
              ),
            ),
            const SizedBox(width: 12),
            if (!isPaid)
              ElevatedButton.icon(
                onPressed: _markAsPaid,
                icon: const Icon(Icons.check_circle_outline, size: 16, color: Colors.white),
                label: const Text('Mark as Paid'),
                style: ElevatedButton.styleFrom(
                  foregroundColor: Colors.white,
                  backgroundColor: _gold,
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                  textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13.5),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildBadge(PaymentStatus status) {
    final isPaid    = status == PaymentStatus.paid;
    final isPartial = status == PaymentStatus.partiallyPaid;
    final isUnpaid  = !isPaid && !isPartial;

    final bg   = isPaid ? const Color(0xFFE6F6EE) : isPartial ? const Color(0xFFFFF7E0) : const Color(0xFFFFECEB);
    final fg   = isPaid ? const Color(0xFF1A7A45) : isPartial ? const Color(0xFFB07A10) : const Color(0xFFB83230);
    final dot  = isPaid ? const Color(0xFF2DAA62) : isPartial ? const Color(0xFFD49A20) : const Color(0xFFE04340);
    final lbl  = isPaid ? 'Paid'                  : isPartial ? 'Partial'               : 'Unpaid';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(20)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 7, height: 7, decoration: BoxDecoration(color: dot, shape: BoxShape.circle)),
          const SizedBox(width: 6),
          Text(lbl, style: TextStyle(color: fg, fontSize: 12.5, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// Styled Container
// ─────────────────────────────────────────────────────────
class _StyledCard extends StatelessWidget {
  final Widget child;
  const _StyledCard({required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(_cardRadius),
        boxShadow: const [_cardShadow],
      ),
      child: child,
    );
  }
}

// ─────────────────────────────────────────────────────────
// Left Column: Invoice Details
// ─────────────────────────────────────────────────────────
class _InvoiceDetailsCard extends StatelessWidget {
  final MechanicInvoice invoice;
  const _InvoiceDetailsCard({required this.invoice});

  @override
  Widget build(BuildContext context) {
    return _StyledCard(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(color: const Color(0xFFFBF4DF), borderRadius: BorderRadius.circular(6)),
                  child: const Icon(Icons.info_outline, color: _gold, size: 16),
                ),
                const SizedBox(width: 12),
                const Text('Invoice Details', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: _ink)),
              ],
            ),
            const SizedBox(height: 24),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(child: _InfoBlock(label: 'Date', value: DateFormat('MMMM dd, yyyy').format(invoice.invoiceDate))),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Plate Number', style: TextStyle(color: _muted, fontSize: 12)),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          border: Border.all(color: const Color(0xFFEEEEEE)),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(invoice.plateNumber, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: _ink, letterSpacing: 0.5)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(child: _InfoBlock(label: 'Labor Charges', value: 'QAR ${invoice.laborCharges.toStringAsFixed(2)}', valueColor: _gold)),
                Expanded(child: _InfoBlock(label: 'Total Amount', value: 'QAR ${invoice.grandTotal.toStringAsFixed(2)}', valueColor: _gold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────
// Right Column: Customer Details
// ─────────────────────────────────────────────────────────
class _CustomerCard extends StatelessWidget {
  final MechanicInvoice invoice;
  final VoidCallback onRefresh;
  const _CustomerCard({required this.invoice, required this.onRefresh});

  @override
  Widget build(BuildContext context) {
    final c = invoice.customer;
    final String initial = c.customerName?.isNotEmpty == true ? c.customerName!.substring(0, 1).toUpperCase() : 'C';

    return _StyledCard(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(color: const Color(0xFFFBF4DF), borderRadius: BorderRadius.circular(6)),
                  child: const Icon(Icons.person_outline, color: _gold, size: 16),
                ),
                const SizedBox(width: 12),
                const Text('Customer', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: _ink)),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: const Color(0xFFF1EAC8),
                  child: Text(initial, style: const TextStyle(color: _gold, fontWeight: FontWeight.w800, fontSize: 18)),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(c.customerName ?? 'Unknown', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16, color: _ink)),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.phone_outlined, size: 14, color: _muted),
                        const SizedBox(width: 4),
                        Text(c.phoneNumber ?? 'No Phone', style: const TextStyle(color: _muted, fontSize: 13)),
                      ],
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            const SizedBox(height: 24),
            _InfoBlock(label: 'QID', value: c.qid ?? '—'),
          ],
        ),
      ),
    );
  }
}

class _InfoBlock extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoBlock({required this.label, required this.value, this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: _gold, fontWeight: FontWeight.w600, fontSize: 12)),
        const SizedBox(height: 6),
        Text(value, style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: valueColor ?? _ink)),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────
// Repair Items Table
// ─────────────────────────────────────────────────────────
class _RepairItemsCard extends StatelessWidget {
  final MechanicInvoice invoice;
  const _RepairItemsCard({required this.invoice});

  @override
  Widget build(BuildContext context) {
    return _StyledCard(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(color: const Color(0xFFFBF4DF), borderRadius: BorderRadius.circular(6)),
                  child: const Icon(Icons.build_outlined, color: _gold, size: 16),
                ),
                const SizedBox(width: 12),
                const Text('Repair Items', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: _ink)),
              ],
            ),
            const SizedBox(height: 24),
            // Header Row
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Row(
                children: const [
                  SizedBox(width: 40, child: Text('#', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600))),
                  Expanded(flex: 3, child: Text('Description', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600))),
                  Expanded(flex: 1, child: Text('Qty', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600))),
                  Expanded(flex: 1, child: Text('Unit Price', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600))),
                  Expanded(flex: 1, child: Text('Commission', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600))),
                  Expanded(flex: 1, child: Align(alignment: Alignment.centerRight, child: Text('Amount (QAR)', style: TextStyle(color: _muted, fontSize: 12, fontWeight: FontWeight.w600)))),
                ],
              ),
            ),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            // Item Rows
            ...invoice.items.asMap().entries.map((entry) {
              final idx = entry.key + 1;
              final item = entry.value;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Row(
                  children: [
                    SizedBox(width: 40, child: Text('$idx', style: const TextStyle(color: _muted, fontSize: 14))),
                    Expanded(flex: 3, child: Text(item.description, style: const TextStyle(fontWeight: FontWeight.w600, color: _ink, fontSize: 14))),
                    Expanded(flex: 1, child: Text('${item.quantity.toInt()}', style: const TextStyle(color: _gold, fontWeight: FontWeight.w600, fontSize: 14))),
                    Expanded(flex: 1, child: Text(item.unitPrice.toStringAsFixed(2), style: const TextStyle(color: _ink, fontSize: 14))),
                    Expanded(flex: 1, child: Text(item.commission.toStringAsFixed(2), style: const TextStyle(color: _ink, fontSize: 14))),
                    Expanded(flex: 1, child: Align(alignment: Alignment.centerRight, child: Text(item.total.toStringAsFixed(2), style: const TextStyle(fontWeight: FontWeight.w700, color: _ink, fontSize: 14)))),
                  ],
                ),
              );
            }).toList(),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            const SizedBox(height: 24),
            // Totals
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                SizedBox(
                  width: 320,
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Subtotal', style: TextStyle(color: _muted, fontSize: 13)),
                          Text('QAR ${invoice.subtotal.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w600, color: _ink, fontSize: 14)),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: const [
                              Text('Papay Charges', style: TextStyle(color: _gold, fontWeight: FontWeight.w600, fontSize: 13)),
                              Text(' * required', style: TextStyle(color: _goldDark, fontSize: 11)),
                            ],
                          ),
                          Text('QAR ${invoice.laborCharges.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w600, color: _ink, fontSize: 14)),
                        ],
                      ),
                      const SizedBox(height: 24),
                      const Divider(height: 1, color: Color(0xFFF0F0F0)),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('TOTAL ONLY', style: TextStyle(fontWeight: FontWeight.w800, color: _ink, fontSize: 16)),
                          Text('QR ${invoice.grandTotal.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w800, color: _gold, fontSize: 18)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

