import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/insurance_state.dart';
import '../models/insurance_models.dart';

// ──────────────────────────────────────────────
// Design tokens  (mirrors the React palette)
// ──────────────────────────────────────────────
const _gold = Color(0xFFB8863A);
const _goldDark = Color(0xFF9C6F2C);
const _goldSoft = Color(0xFFF5EAD4);
const _ink = Color(0xFF1C1812);
const _muted = Color(0xFF9A9080);
const _border = Color(0xFFE8E1D4);
const _bg = Color(0xFFEEE9DF);
const _cardBg = Color(0xFFFFFFFF);
const _inputBg = Color(0xFFFCFBF8);
const _placeholder = Color(0xFFC4BDB1);

// ──────────────────────────────────────────────
// Item row model
// ──────────────────────────────────────────────
class _ItemRow {
  int? id;
  final TextEditingController description = TextEditingController();
  final TextEditingController quantity = TextEditingController(text: '1');
  final TextEditingController unitPrice = TextEditingController();
  final TextEditingController commission = TextEditingController();

  void dispose() {
    description.dispose();
    quantity.dispose();
    unitPrice.dispose();
    commission.dispose();
  }

  Map<String, dynamic> toJson() => {
        'description': description.text.trim(),
        'quantity': double.tryParse(quantity.text) ?? 1,
        'unit_price': double.tryParse(unitPrice.text) ?? 0,
        'commission': double.tryParse(commission.text) ?? 0,
      };

  bool get isValid =>
      description.text.trim().isNotEmpty &&
      (double.tryParse(quantity.text) ?? 0) > 0 &&
      double.tryParse(unitPrice.text) != null;

  double get amount =>
      ((double.tryParse(quantity.text) ?? 0) *
      (double.tryParse(unitPrice.text) ?? 0)) +
      (double.tryParse(commission.text) ?? 0);
}

// ──────────────────────────────────────────────
// Screen
// ──────────────────────────────────────────────
class EditInvoiceScreen extends StatefulWidget {
  final InsuranceInvoice invoice;
  const EditInvoiceScreen({super.key, required this.invoice});

  @override
  State<EditInvoiceScreen> createState() => _EditInvoiceScreenState();
}

class _EditInvoiceScreenState extends State<EditInvoiceScreen> {
  final _formKey = GlobalKey<FormState>();

  final _plateController = TextEditingController();
  final _laborController = TextEditingController();
  String _paymentStatus = 'UNPAID';

  final _customerNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _qidController = TextEditingController();

  final List<_ItemRow> _items = [];
  final List<int> _deletedItemIds = [];

  @override
  void initState() {
    super.initState();
    _plateController.text = widget.invoice.plateNumber;
    _laborController.text = widget.invoice.laborCharges == 0 ? '' : widget.invoice.laborCharges.toStringAsFixed(2);
    _paymentStatus = paymentStatusToString(widget.invoice.paymentStatus);
    
    _customerNameController.text = widget.invoice.customer.customerName ?? '';
    _phoneController.text = widget.invoice.customer.phoneNumber ?? '';
    _qidController.text = widget.invoice.customer.qid ?? '';

    for (final item in widget.invoice.items) {
      final row = _ItemRow();
      row.id = item.id;
      row.description.text = item.description;
      row.quantity.text = item.quantity.toString();
      row.unitPrice.text = item.unitPrice.toString();
      row.commission.text = item.commission == 0 ? '' : item.commission.toString();
      _items.add(row);
    }
  }

  double get _subtotal => _items.fold(0, (s, i) => s + i.amount);
  double get _labor => double.tryParse(_laborController.text) ?? 0;
  double get _total => _subtotal + _labor;

  @override
  void dispose() {
    _plateController.dispose();
    _laborController.dispose();
    _customerNameController.dispose();
    _phoneController.dispose();
    _qidController.dispose();
    for (final item in _items) {
      item.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_items.isNotEmpty && !_items.every((i) => i.isValid)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please fill in all item fields correctly.')),
      );
      return;
    }

    final state = context.read<InsuranceState>();
    bool changed = false;

    // Customer
    final cust = widget.invoice.customer;
    if (_customerNameController.text.trim() != (cust.customerName ?? '') ||
        _phoneController.text.trim() != (cust.phoneNumber ?? '') ||
        _qidController.text.trim() != (cust.qid ?? '')) {
      await state.updateCustomer(cust.id, {
        'customer_name': _customerNameController.text.trim().isEmpty ? null : _customerNameController.text.trim(),
        'phone_number': _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
        'qid': _qidController.text.trim().isEmpty ? null : _qidController.text.trim(),
      });
      changed = true;
    }

    // Invoice
    final labor = double.tryParse(_laborController.text) ?? 0;
    if (_plateController.text.trim() != widget.invoice.plateNumber ||
        labor != widget.invoice.laborCharges ||
        _paymentStatus != paymentStatusToString(widget.invoice.paymentStatus)) {
      await state.updateInvoice(widget.invoice.id, {
        'plate_number': _plateController.text.trim(),
        'labor_charges': labor,
        'payment_status': _paymentStatus,
      });
      changed = true;
    }

    // Deleted items
    for (final id in _deletedItemIds) {
      await state.deleteItem(id);
      changed = true;
    }

    // Existing & New Items
    for (final i in _items) {
      if (i.id != null) {
        // existing item, check if changed
        final orig = widget.invoice.items.firstWhere((x) => x.id == i.id);
        final currentQty = double.tryParse(i.quantity.text) ?? 0;
        final currentPrice = double.tryParse(i.unitPrice.text) ?? 0;
        final currentComm = double.tryParse(i.commission.text) ?? 0;
        final currentDesc = i.description.text.trim();

        if (orig.description != currentDesc ||
            orig.quantity != currentQty ||
            orig.unitPrice != currentPrice ||
            orig.commission != currentComm) {
          await state.updateItem(i.id!, {
            'description': currentDesc,
            'quantity': currentQty,
            'unit_price': currentPrice,
            'commission': currentComm,
          });
          changed = true;
        }
      } else {
        // new item
        await state.createItem(widget.invoice.id, i.toJson());
        changed = true;
      }
    }

    if (!mounted) return;
    
    if (state.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(state.errorMessage!),
            backgroundColor: const Color(0xFFB04A3C)),
      );
    } else {
      if (changed) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('Invoice #${widget.invoice.id} updated!'),
              backgroundColor: const Color(0xFF3E8E5E)),
        );
      }
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.select((InsuranceState s) => s.isLoading);

    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _TopBar(isLoading: isLoading, onSave: _submit),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(24, 20, 24, 40),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _SectionCard(
                        icon: Icons.person_outline_rounded,
                        title: 'Customer Details',
                        child: _buildCustomerFields(),
                      ),
                      const SizedBox(height: 20),
                      _SectionCard(
                        icon: Icons.receipt_long_outlined,
                        title: 'Invoice Details',
                        child: _buildInvoiceFields(),
                      ),
                      const SizedBox(height: 20),
                      _SectionCard(
                        icon: Icons.build_outlined,
                        title: 'Items',
                        trailing: _AddItemButton(
                          onTap: () => setState(() => _items.add(_ItemRow())),
                        ),
                        child: _buildItemsTable(),
                      ),
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

  // ── Customer fields ───────────────────────────────────────────────────────

  Widget _buildCustomerFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _FieldLabel(label: 'Customer Name', hint: '(optional)'),
        const SizedBox(height: 6),
        _GoldInput(
          controller: _customerNameController,
          hint: 'e.g. Mustafa Al-Sayed',
        ),
        const SizedBox(height: 18),
        Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _FieldLabel(label: 'Phone Number', hint: '(optional)'),
                  const SizedBox(height: 6),
                  _GoldInput(
                    controller: _phoneController,
                    hint: '3XXXXXXX',
                    prefixIcon: Icons.phone_outlined,
                    keyboardType: TextInputType.phone,
                    validator: (v) {
                      if (v != null && v.trim().isNotEmpty) {
                        if (v.trim().length != 8 || int.tryParse(v.trim()) == null) {
                          return '8 digits';
                        }
                      }
                      return null;
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _FieldLabel(label: 'QID', hint: '(optional)'),
                  const SizedBox(height: 6),
                  _GoldInput(
                    controller: _qidController,
                    hint: '28XXXXXXXXXX',
                    prefixIcon: Icons.credit_card_outlined,
                    validator: (v) {
                      if (v != null && v.trim().isNotEmpty) {
                        if (v.trim().length != 11 || int.tryParse(v.trim()) == null) {
                          return '11 digits';
                        }
                      }
                      return null;
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ── Invoice fields ────────────────────────────────────────────────────────

  Widget _buildInvoiceFields() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _FieldLabel(label: 'Plate Number', required: true),
              const SizedBox(height: 6),
              _GoldInput(
                controller: _plateController,
                hint: 'e.g. 771775',
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Required';
                  if (v.trim().length > 6 || int.tryParse(v.trim()) == null) return '1-6 digits';
                  return null;
                },
              ),
            ],
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _FieldLabel(label: 'Labor Charges'),
              const SizedBox(height: 6),
              _GoldInput(
                controller: _laborController,
                hint: 'QAR 0.00',
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
                ],
                onChanged: (_) => setState(() {}),
              ),
            ],
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _FieldLabel(label: 'Payment Status'),
              const SizedBox(height: 6),
              _StatusDropdown(
                value: _paymentStatus,
                onChanged: (v) => setState(() => _paymentStatus = v!),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ── Items table ───────────────────────────────────────────────────────────

  Widget _buildItemsTable() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 10),
          child: Row(
            children: [
              SizedBox(width: 28, child: _ColHeader('#')),
              SizedBox(width: 8),
              Expanded(flex: 4, child: _ColHeader('Description')),
              SizedBox(width: 8),
              SizedBox(width: 70, child: _ColHeader('Qty')),
              SizedBox(width: 8),
              SizedBox(width: 110, child: _ColHeader('Unit Price')),
              SizedBox(width: 8),
              SizedBox(width: 110, child: _ColHeader('Commission')),
              SizedBox(width: 8),
              SizedBox(width: 90, child: _ColHeader('Amount', right: true)),
              SizedBox(width: 40),
            ],
          ),
        ),
        const Divider(color: _border, height: 1, thickness: 1.5),
        const SizedBox(height: 6),
        ...List.generate(_items.length, (idx) {
          final item = _items[idx];
          return _ItemTableRow(
            index: idx,
            item: item,
            canRemove: true,
            onRemove: () => setState(() {
              if (item.id != null) {
                _deletedItemIds.add(item.id!);
              }
              item.dispose();
              _items.removeAt(idx);
            }),
            onChanged: () => setState(() {}),
          );
        }),
        const SizedBox(height: 16),
        const Divider(color: _border, height: 1, thickness: 1),
        const SizedBox(height: 20),
        Align(
          alignment: Alignment.centerRight,
          child: SizedBox(
            width: 280,
            child: Column(
              children: [
                _TotalRow(label: 'Subtotal', value: _subtotal),
                const SizedBox(height: 10),
                _TotalRow(label: 'Labor Charges', value: _labor),
                const SizedBox(height: 12),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: _goldSoft,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Total',
                        style: TextStyle(
                            fontSize: 14.5,
                            fontWeight: FontWeight.w800,
                            color: _ink),
                      ),
                      Text(
                        'QAR ${_total.toStringAsFixed(2)}',
                        style: const TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                            color: _goldDark),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Reusable sub-widgets
// ──────────────────────────────────────────────────────────────────────────────

class _TopBar extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onSave;
  const _TopBar({required this.isLoading, required this.onSave});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _bg,
      padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 24),
      child: Row(
        children: [
          OutlinedButton(
            onPressed: () => Navigator.pop(context),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.all(20),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              side: const BorderSide(color: _border, width: 1.5),
              backgroundColor: _cardBg,
              foregroundColor: _ink,
            ),
            child: const Icon(Icons.arrow_back, size: 20, color: _ink),
          ),
          const SizedBox(width: 20),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Edit Insurance Invoice',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                    color: _ink,
                    letterSpacing: -0.5,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Update the details of the invoice below',
                  style: TextStyle(fontSize: 14.5, color: _muted),
                ),
              ],
            ),
          ),
          ElevatedButton.icon(
            onPressed: isLoading ? null : onSave,
            icon: isLoading
                ? const SizedBox(
                    width: 16, height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.save_outlined, size: 18),
            label: const Text('Update Invoice'),
            style: ElevatedButton.styleFrom(
              foregroundColor: Colors.white,
              backgroundColor: _gold,
              disabledBackgroundColor: _gold.withOpacity(0.5),
              disabledForegroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              textStyle: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w700),
            ).copyWith(
              backgroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.disabled)) return _gold.withOpacity(0.5);
                if (states.contains(WidgetState.hovered)) return _goldDark;
                return _gold;
              }),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget child;
  final Widget? trailing;

  const _SectionCard({
    required this.icon,
    required this.title,
    required this.child,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _border),
        boxShadow: const [
          BoxShadow(
              color: Color(0x05211D16), blurRadius: 2, offset: Offset(0, 1)),
          BoxShadow(
              color: Color(0x08211D16), blurRadius: 24, offset: Offset(0, 8)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(28, 24, 28, 20),
            child: Row(
              children: [
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: _goldSoft,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, size: 20, color: _goldDark),
                ),
                const SizedBox(width: 14),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: _ink,
                    letterSpacing: -0.15,
                  ),
                ),
                const Spacer(),
                if (trailing != null) trailing!,
              ],
            ),
          ),
          const Divider(color: _border, height: 1, thickness: 1),
          Padding(padding: const EdgeInsets.all(24), child: child),
        ],
      ),
    );
  }
}

class _AddItemButton extends StatelessWidget {
  final VoidCallback onTap;
  const _AddItemButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: _goldSoft,
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.add, size: 16, color: _goldDark),
            SizedBox(width: 6),
            Text(
              'Add Item',
              style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: _goldDark),
            ),
          ],
        ),
      ),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  final String label;
  final String? hint;
  final bool required;

  const _FieldLabel(
      {required this.label, this.hint, this.required = false});

  @override
  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        style: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.6,
          color: _goldDark,
        ),
        text: label.toUpperCase(),
        children: [
          if (required)
            const TextSpan(text: ' *', style: TextStyle(color: _gold)),
          if (hint != null)
            TextSpan(
              text: ' $hint',
              style: const TextStyle(
                  fontWeight: FontWeight.w400,
                  letterSpacing: 0,
                  color: _muted,
                  fontSize: 12),
            ),
        ],
      ),
    );
  }
}

class _GoldInput extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final String? prefixText;
  final IconData? prefixIcon;
  final TextInputType? keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final String? Function(String?)? validator;
  final ValueChanged<String>? onChanged;

  const _GoldInput({
    required this.controller,
    required this.hint,
    this.prefixText,
    this.prefixIcon,
    this.keyboardType,
    this.inputFormatters,
    this.validator,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      validator: validator,
      style: const TextStyle(fontSize: 14.5, color: _ink),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: _placeholder, fontSize: 14.5),
        prefixText: prefixText,
        prefixStyle: const TextStyle(
            color: _muted, fontSize: 13, fontWeight: FontWeight.w600),
        prefixIcon: prefixIcon != null
            ? Icon(prefixIcon, size: 16, color: _muted)
            : null,
        filled: true,
        fillColor: _inputBg,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _border, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _border, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _gold, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              const BorderSide(color: Color(0xFFB04A3C), width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide:
              const BorderSide(color: Color(0xFFB04A3C), width: 1.5),
        ),
      ),
    );
  }
}

class _StatusDropdown extends StatelessWidget {
  final String value;
  final ValueChanged<String?> onChanged;
  const _StatusDropdown({required this.value, required this.onChanged});

  Color get _textColor {
    switch (value) {
      case 'PAID':
        return const Color(0xFF3E8E5E);
      default:
        return const Color(0xFFB04A3C);
    }
  }

  Color get _bgColor {
    switch (value) {
      case 'PAID':
        return const Color(0xFFE7F4EC);
      default:
        return const Color(0xFFF7E7E3);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: _bgColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _border, width: 1.5),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isDense: true,
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down_rounded,
              color: _textColor, size: 20),
          style: TextStyle(
              fontSize: 14.5,
              fontWeight: FontWeight.w700,
              color: _textColor),
          dropdownColor: Colors.white,
          onChanged: onChanged,
          items: const [
            DropdownMenuItem(
              value: 'UNPAID',
              child: Text('Unpaid',
                  style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: Color(0xFFB04A3C))),
            ),
            DropdownMenuItem(
              value: 'PAID',
              child: Text('Paid',
                  style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF3E8E5E))),
            ),
          ],
        ),
      ),
    );
  }
}

class _ColHeader extends StatelessWidget {
  final String text;
  final bool right;
  const _ColHeader(this.text, {this.right = false});

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      textAlign: right ? TextAlign.right : TextAlign.left,
      style: const TextStyle(
        fontSize: 11.5,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.6,
        color: _muted,
      ),
    );
  }
}

class _ItemTableRow extends StatelessWidget {
  final int index;
  final _ItemRow item;
  final bool canRemove;
  final VoidCallback onRemove;
  final VoidCallback onChanged;

  const _ItemTableRow({
    required this.index,
    required this.item,
    required this.canRemove,
    required this.onRemove,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final amount = item.amount;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            height: 38,
            alignment: Alignment.centerLeft,
            width: 28,
            child: Text(
              '${index + 1}',
              style: const TextStyle(
                  fontSize: 13.5,
                  fontWeight: FontWeight.w600,
                  color: _muted),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            flex: 4,
            child: _TableInput(
              controller: item.description,
              hint: 'e.g. Oil Change',
              onChanged: (_) => onChanged(),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Required' : null,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 70,
            child: _TableInput(
              controller: item.quantity,
              hint: '1',
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              onChanged: (_) => onChanged(),
              validator: (v) =>
                  ((double.tryParse(v ?? '') ?? 0) <= 0) ? '!' : null,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 110,
            child: _TableInput(
              controller: item.unitPrice,
              hint: '0.00',
              prefixText: 'QAR ',
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              onChanged: (_) => onChanged(),
              validator: (v) =>
                  (double.tryParse(v ?? '') == null) ? '!' : null,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 110,
            child: _TableInput(
              controller: item.commission,
              hint: 'QAR 0.00',
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
              ],
              onChanged: (_) => onChanged(),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            height: 38,
            alignment: Alignment.centerRight,
            width: 90,
            child: Text(
              amount > 0 ? amount.toStringAsFixed(2) : '—',
              textAlign: TextAlign.right,
              style: const TextStyle(
                  fontSize: 14.5,
                  fontWeight: FontWeight.w700,
                  color: _ink),
            ),
          ),
          Container(
            height: 38,
            alignment: Alignment.center,
            width: 40,
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: canRemove ? onRemove : null,
              icon: const Icon(Icons.remove_circle_outline_rounded),
              color: const Color(0xFFC0594A),
              disabledColor: _border,
              iconSize: 20,
              tooltip: 'Remove',
              splashRadius: 18,
            ),
          ),
        ],
      ),
    );
  }
}

class _TableInput extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final String? prefixText;
  final TextInputType? keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final ValueChanged<String>? onChanged;
  final String? Function(String?)? validator;

  const _TableInput({
    required this.controller,
    required this.hint,
    this.prefixText,
    this.keyboardType,
    this.inputFormatters,
    this.onChanged,
    this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      validator: validator,
      style: const TextStyle(fontSize: 13.5, color: _ink),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: _placeholder, fontSize: 13.5),
        prefixText: prefixText,
        prefixStyle: const TextStyle(
            color: _muted, fontSize: 12, fontWeight: FontWeight.w600),
        filled: true,
        fillColor: _inputBg,
        isDense: true,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _border, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _border, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _gold, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFB04A3C), width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFB04A3C), width: 1.5),
        ),
        errorStyle: const TextStyle(fontSize: 10),
      ),
    );
  }
}

class _TotalRow extends StatelessWidget {
  final String label;
  final double value;
  const _TotalRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: const TextStyle(fontSize: 14, color: _muted)),
        Text(
          'QAR ${value.toStringAsFixed(2)}',
          style: const TextStyle(
              fontSize: 14, fontWeight: FontWeight.w600, color: _ink),
        ),
      ],
    );
  }
}
