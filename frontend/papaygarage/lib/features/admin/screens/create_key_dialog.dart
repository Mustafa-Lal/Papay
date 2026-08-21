import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/admin_state.dart';
import '../models/access_key_model.dart';

class CreateKeyDialog extends StatefulWidget {
  const CreateKeyDialog({super.key});

  @override
  State<CreateKeyDialog> createState() => _CreateKeyDialogState();
}

class _CreateKeyDialogState extends State<CreateKeyDialog> with SingleTickerProviderStateMixin {
  int _selectedRoleId = 1;
  AccessKeyCreateResponse? _createdKey;
  bool _isCopied = false;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 160),
    );
    _scaleAnimation = Tween<double>(begin: 0.98, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: Dialog(
        backgroundColor: Colors.transparent,
        elevation: 0,
        child: Container(
          width: 400,
          padding: const EdgeInsets.fromLTRB(28, 32, 28, 28),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFFFF),
            border: Border.all(color: const Color(0xFFE4E7EA)),
            borderRadius: BorderRadius.circular(16),
            boxShadow: const [
              BoxShadow(
                color: Color.fromRGBO(20, 24, 28, 0.22),
                blurRadius: 70,
                offset: Offset(0, 24),
              ),
            ],
          ),
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              _createdKey != null ? _buildSuccessView() : _buildFormView(),
              // Close button
              Positioned(
                top: -18,
                right: -14,
                child: IconButton(
                  icon: const Icon(Icons.close, size: 18),
                  color: const Color(0xFF6B7280),
                  splashRadius: 20,
                  onPressed: () => Navigator.of(context).pop(),
                  tooltip: 'Close',
                  style: IconButton.styleFrom(
                    hoverColor: const Color(0xFFF1F2F3),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(7)),
                    minimumSize: const Size(28, 28),
                    padding: EdgeInsets.zero,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFormView() {
    final isLoading = context.select((AdminState state) => state.isLoading);
    final error = context.select((AdminState state) => state.errorMessage);

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Create Access Key',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w600,
            color: Color(0xFF1C2024),
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Select a role for the new user key.',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 13,
            color: Color(0xFF6B7280),
            height: 1.5,
          ),
        ),
        const SizedBox(height: 22),
        if (error != null) ...[
          Text(error, style: const TextStyle(color: Color(0xFFC4453A), fontSize: 13)),
          const SizedBox(height: 16),
        ],
        DropdownButtonFormField<int>(
          value: _selectedRoleId,
          decoration: InputDecoration(
            labelText: 'Role',
            filled: true,
            fillColor: const Color(0xFFFAFAFA),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFE4E7EA)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFB4770A), width: 1.5),
            ),
          ),
          items: const [
            DropdownMenuItem(value: 1, child: Text('Insurance')),
            DropdownMenuItem(value: 2, child: Text('Mechanic')),
            DropdownMenuItem(value: 3, child: Text('Owner')),
            DropdownMenuItem(value: 4, child: Text('Admin')),
          ],
          onChanged: isLoading ? null : (value) {
            if (value != null) {
              setState(() => _selectedRoleId = value);
            }
          },
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            Expanded(
              child: TextButton(
                onPressed: isLoading ? null : () => Navigator.of(context).pop(),
                style: TextButton.styleFrom(
                  foregroundColor: const Color(0xFF6B7280),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('Cancel', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: isLoading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFB4770A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  elevation: 0,
                ),
                child: isLoading
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Create', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        )
      ],
    );
  }

  Widget _buildSuccessView() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(
          child: Container(
            width: 44,
            height: 44,
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: const Color.fromRGBO(47, 147, 102, 0.10),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.check, color: Color(0xFF2F9366), size: 20),
          ),
        ),
        const Text(
          'Key created',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w600,
            color: Color(0xFF1C2024),
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Share this key with the user. It won\'t be shown again after you close this window.',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 13,
            color: Color(0xFF6B7280),
            height: 1.5,
          ),
        ),
        const SizedBox(height: 22),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
          decoration: BoxDecoration(
            color: const Color(0xFFFAFAFA),
            border: Border.all(color: const Color(0xFFE4E7EA)),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Text(
                    _createdKey!.rawKey,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 0.08 * 14,
                      color: Color(0xFF1C2024),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              OutlinedButton.icon(
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: _createdKey!.rawKey));
                  setState(() => _isCopied = true);
                  Future.delayed(const Duration(milliseconds: 1800), () {
                    if (mounted) setState(() => _isCopied = false);
                  });
                },
                style: OutlinedButton.styleFrom(
                  backgroundColor: _isCopied ? const Color.fromRGBO(47, 147, 102, 0.10) : const Color(0xFFFFFFFF),
                  foregroundColor: _isCopied ? const Color(0xFF2F9366) : const Color(0xFF1C2024),
                  side: BorderSide(color: _isCopied ? Colors.transparent : const Color(0xFFE4E7EA)),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  minimumSize: Size.zero,
                  elevation: 0,
                ),
                icon: Icon(Icons.copy, size: 13),
                label: Text(
                  _isCopied ? 'Copied' : 'Copy',
                  style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () => Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFB4770A),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            elevation: 0,
          ),
          child: const Text('Done', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
        ),
      ],
    );
  }

  Future<void> _submit() async {
    final state = context.read<AdminState>();
    final response = await state.createKey(_selectedRoleId);
    if (response != null && mounted) {
      setState(() {
        _createdKey = response;
      });
    }
  }
}
