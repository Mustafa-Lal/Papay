import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:image_picker/image_picker.dart';
import '../models/insurance_models.dart';
import '../providers/insurance_state.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../utils/invoice_printer.dart';
import 'edit_invoice_screen.dart';
export '../providers/insurance_state.dart';

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

class InvoiceDetailScreen extends StatefulWidget {
  final int invoiceId;
  const InvoiceDetailScreen({super.key, required this.invoiceId});

  @override
  State<InvoiceDetailScreen> createState() => _InvoiceDetailScreenState();
}

class _InvoiceDetailScreenState extends State<InvoiceDetailScreen> {
  InsuranceInvoice? _invoice;
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
    final state = context.read<InsuranceState>();
    final inv = await state.getInvoiceDetail(widget.invoiceId);
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

    final state = context.read<InsuranceState>();
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
                  const SizedBox(height: 24),
                  _ImagesCard(invoice: inv, onRefresh: _load),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(InsuranceInvoice inv) {
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
              'Generated on ${DateFormat('MMMM dd, yyyy').format(inv.createdAt)}',
              style: const TextStyle(fontSize: 15, color: _muted),
            ),
          ],
        ),
        Row(
          children: [
            OutlinedButton.icon(
              onPressed: () {
                if (_invoice != null) {
                  printInsuranceInvoice(context, _invoice!);
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
  final InsuranceInvoice invoice;
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
                Expanded(child: _InfoBlock(label: 'Date', value: DateFormat('MMMM dd, yyyy').format(invoice.createdAt))),
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
  final InsuranceInvoice invoice;
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
  final InsuranceInvoice invoice;
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

// ─────────────────────────────────────────────────────────
// Images Section
// ─────────────────────────────────────────────────────────
class _ImagesCard extends StatefulWidget {
  final InsuranceInvoice invoice;
  final VoidCallback onRefresh;
  const _ImagesCard({required this.invoice, required this.onRefresh});

  @override
  State<_ImagesCard> createState() => _ImagesCardState();
}

class _ImagesCardState extends State<_ImagesCard> {
  bool _uploading = false;

  Future<void> _pickAndUpload() async {
    // ... [Same logic as before]
    final imageType = await showDialog<String>(
      context: context,
      builder: (ctx) => SimpleDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Select Image Type', style: TextStyle(fontWeight: FontWeight.w700)),
        children: [
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, 'BEFORE'),
            child: const Padding(padding: EdgeInsets.symmetric(vertical: 8.0), child: Text('Before Repair', style: TextStyle(fontSize: 16))),
          ),
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, 'AFTER'),
            child: const Padding(padding: EdgeInsets.symmetric(vertical: 8.0), child: Text('After Repair', style: TextStyle(fontSize: 16))),
          ),
        ],
      ),
    );
    if (imageType == null) return;

    final source = await showDialog<ImageSource>(
      context: context,
      builder: (ctx) => SimpleDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Select Image Source', style: TextStyle(fontWeight: FontWeight.w700)),
        children: [
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, ImageSource.gallery),
            child: const Padding(padding: EdgeInsets.symmetric(vertical: 8.0), child: Row(children: [Icon(Icons.photo_library, color: _muted), SizedBox(width: 12), Text('Gallery', style: TextStyle(fontSize: 16))])),
          ),
          SimpleDialogOption(
            onPressed: () => Navigator.pop(ctx, ImageSource.camera),
            child: const Padding(padding: EdgeInsets.symmetric(vertical: 8.0), child: Row(children: [Icon(Icons.camera_alt, color: _muted), SizedBox(width: 12), Text('Camera', style: TextStyle(fontSize: 16))])),
          ),
        ],
      ),
    );
    if (source == null) return;

    final picker = ImagePicker();
    XFile? file;
    try {
      file = await picker.pickImage(source: source);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Camera not supported. Try Gallery.')));
      return;
    }
    if (file == null) return;

    setState(() => _uploading = true);
    try {
      final bytes = await file.readAsBytes();
      if (!mounted) return;
      final newImage = await context.read<InsuranceState>().uploadImage(
        invoiceId: widget.invoice.id,
        imageType: imageType,
        filename: file.name,
        bytes: bytes.toList(),
      );
      if (newImage != null && mounted) {
        setState(() => widget.invoice.images.add(newImage));
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(children: [
              const Icon(Icons.check_circle_outline, color: Colors.white, size: 18),
              const SizedBox(width: 10),
              Text('Successfully uploaded ${imageType == 'BEFORE' ? 'Before' : 'After'} image'),
            ]),
            backgroundColor: const Color(0xFF1F9D55),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final beforeImages = widget.invoice.images.where((i) => i.imageType == 'BEFORE').toList();
    final afterImages = widget.invoice.images.where((i) => i.imageType == 'AFTER').toList();

    return _StyledCard(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(color: const Color(0xFFFBF4DF), borderRadius: BorderRadius.circular(6)),
                      child: const Icon(Icons.image_outlined, color: _gold, size: 16),
                    ),
                    const SizedBox(width: 12),
                    Text('Images (${widget.invoice.images.length})', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: _ink)),
                  ],
                ),
                _uploading
                    ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2, color: _gold))
                    : ElevatedButton.icon(
                        onPressed: _pickAndUpload,
                        icon: const Icon(Icons.upload_outlined, size: 14),
                        label: const Text('Upload'),
                        style: ElevatedButton.styleFrom(
                          foregroundColor: Colors.white,
                          backgroundColor: _gold,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                        ),
                      ),
              ],
            ),
            const SizedBox(height: 24),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: () {
                    if (beforeImages.isNotEmpty) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => _FullScreenImageViewer(
                          images: beforeImages,
                          initialIndex: 0,
                          onDelete: (img) => setState(() => widget.invoice.images.removeWhere((i) => i.id == img.id)),
                        )),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('No Before images uploaded yet.')));
                    }
                  },
                  icon: const Icon(Icons.image_search, size: 16),
                  label: Text('View Before (${beforeImages.length})'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: _muted,
                    side: const BorderSide(color: Color(0xFFE5E5E5)),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: () {
                    if (afterImages.isNotEmpty) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => _FullScreenImageViewer(
                          images: afterImages,
                          initialIndex: 0,
                          onDelete: (img) => setState(() => widget.invoice.images.removeWhere((i) => i.id == img.id)),
                        )),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('No After images uploaded yet.')));
                    }
                  },
                  icon: const Icon(Icons.image_search, size: 16),
                  label: Text('View After (${afterImages.length})'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: _muted,
                    side: const BorderSide(color: Color(0xFFE5E5E5)),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
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

// _ImageTile removed — thumbnails no longer shown in the card view.
// Images are only viewable via the full-screen viewer.

class _FullScreenImageViewer extends StatefulWidget {
  final List<InsuranceImage> images;
  final int initialIndex;
  final void Function(InsuranceImage) onDelete;

  const _FullScreenImageViewer({
    required this.images,
    required this.initialIndex,
    required this.onDelete,
  });

  @override
  State<_FullScreenImageViewer> createState() => _FullScreenImageViewerState();
}

class _FullScreenImageViewerState extends State<_FullScreenImageViewer> {
  late PageController _pageController;
  late List<InsuranceImage> _images;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _images = List.from(widget.images);
    _currentIndex = widget.initialIndex;
    _pageController = PageController(initialPage: widget.initialIndex);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _deleteCurrentImage() async {
    final image = _images[_currentIndex];
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: const Text('Delete Image', style: TextStyle(fontWeight: FontWeight.w700)),
        content: const Text('Are you sure you want to delete this image?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.pop(ctx, true), style: TextButton.styleFrom(foregroundColor: Colors.red), child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true || !mounted) return;

    await context.read<InsuranceState>().deleteImage(image.id);
    widget.onDelete(image);

    setState(() {
      _images.removeAt(_currentIndex);
      if (_images.isEmpty) {
        Navigator.pop(context);
        return;
      }
      _currentIndex = _currentIndex.clamp(0, _images.length - 1);
    });
    // Jump controller to corrected index without animation
    _pageController.jumpToPage(_currentIndex);
  }

  @override
  Widget build(BuildContext context) {
    final client = context.read<ApiClient>();

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        title: Text(
          '${_currentIndex + 1} / ${_images.length}',
          style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w600),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
            tooltip: 'Delete image',
            onPressed: _deleteCurrentImage,
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: PageView.builder(
        controller: _pageController,
        itemCount: _images.length,
        onPageChanged: (i) => setState(() => _currentIndex = i),
        itemBuilder: (context, index) {
          final image = _images[index];
          final imageUrl = '${ApiEndpoints.baseUrl}/insurance/images/${image.id}';
          
          return FutureBuilder(
            future: client.buildHeaders(),
            builder: (ctx, snapshot) {
              if (!snapshot.hasData) return const Center(child: CircularProgressIndicator(color: Colors.white));
              return InteractiveViewer(
                child: Center(
                  child: Image.network(
                    imageUrl,
                    headers: snapshot.data!,
                    fit: BoxFit.contain,
                    errorBuilder: (_, __, ___) => const Icon(Icons.broken_image_outlined, color: Colors.grey, size: 64),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
