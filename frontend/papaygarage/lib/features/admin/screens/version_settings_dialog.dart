import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/admin_state.dart';

class VersionSettingsDialog extends StatefulWidget {
  const VersionSettingsDialog({super.key});

  @override
  State<VersionSettingsDialog> createState() => _VersionSettingsDialogState();
}

class _VersionSettingsDialogState extends State<VersionSettingsDialog> {
  final _versionController = TextEditingController();
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final state = context.read<AdminState>();
    final version = await state.fetchRequiredVersion();
    if (mounted) {
      setState(() {
        _versionController.text = version;
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _versionController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final version = _versionController.text.trim();
    if (version.isEmpty) return;

    setState(() => _isLoading = true);
    final state = context.read<AdminState>();
    final success = await state.updateRequiredVersion(version);
    
    if (mounted) {
      setState(() => _isLoading = false);
      if (success) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Required app version updated successfully.')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(state.errorMessage ?? 'Failed to update version.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: 400,
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'System Settings',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: Color(0xFF1C2024),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Update the minimum required app version for all users.',
              style: TextStyle(
                fontSize: 13,
                color: Color(0xFF6B7280),
              ),
            ),
            const SizedBox(height: 24),
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else
              TextField(
                controller: _versionController,
                decoration: const InputDecoration(
                  labelText: 'Required Version (e.g., 1.5.0)',
                  border: OutlineInputBorder(),
                ),
              ),
            const SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: _isLoading ? null : _save,
                  child: const Text('Save'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
