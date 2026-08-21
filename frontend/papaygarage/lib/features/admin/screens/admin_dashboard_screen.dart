import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_state.dart';
import '../providers/admin_state.dart';
import '../models/access_key_model.dart';
import 'create_key_dialog.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AdminState>().fetchKeys();
    });
  }

  void _showCreateKeyDialog() {
    showDialog(
      context: context,
      barrierColor: const Color.fromRGBO(20, 24, 28, 0.42),
      builder: (_) => const CreateKeyDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F6F7),
      body: Stack(
        children: [
          // Background Gradient
          Positioned.fill(
            child: DecoratedBox(
              decoration: const BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.topCenter,
                  radius: 1.2,
                  colors: [
                    Color.fromRGBO(180, 119, 10, 0.05),
                    Colors.transparent,
                  ],
                  stops: [0.0, 0.55],
                ),
              ),
            ),
          ),
          Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 32),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildTopbar(context),
                    const SizedBox(height: 28),
                    Expanded(
                      child: _buildCard(context),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopbar(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: const Color.fromRGBO(180, 119, 10, 0.10),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.vpn_key_rounded,
                color: Color(0xFFB4770A),
                size: 19,
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'Welcome, Admin',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1C2024),
                    letterSpacing: -0.18,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Manage account access below',
                  style: TextStyle(
                    fontSize: 12.5,
                    color: Color(0xFF6B7280),
                  ),
                ),
              ],
            ),
          ],
        ),
        OutlinedButton.icon(
          onPressed: () => context.read<AuthState>().logout(),
          style: OutlinedButton.styleFrom(
            backgroundColor: const Color(0xFFFFFFFF),
            foregroundColor: const Color(0xFF1C2024),
            side: const BorderSide(color: Color(0xFFE4E7EA)),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(9),
            ),
            elevation: 0,
            textStyle: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          icon: const Icon(Icons.logout, size: 15),
          label: const Text('Log out'),
        ),
      ],
    );
  }

  Widget _buildCard(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        border: Border.all(color: const Color(0xFFE4E7EA)),
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Color.fromRGBO(20, 24, 28, 0.06),
            blurRadius: 40,
            offset: Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Card Header
          Container(
            padding: const EdgeInsets.fromLTRB(24, 20, 24, 16),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: Color(0xFFE4E7EA))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text(
                        'User accounts',
                        style: TextStyle(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1C2024),
                        ),
                      ),
                      SizedBox(height: 3),
                      Text(
                        'Activate or deactivate access by role',
                        style: TextStyle(
                          fontSize: 12.5,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _showCreateKeyDialog,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFB4770A),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 20),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(9),
                    ),
                    elevation: 0,
                    textStyle: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  icon: const Icon(Icons.add, size: 15),
                  label: const Text('Create key'),
                ),
              ],
            ),
          ),
          // Table
          Expanded(
            child: Consumer<AdminState>(
              builder: (context, state, child) {
                if (state.isLoading && state.keys.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (state.errorMessage != null && state.keys.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(state.errorMessage!, style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () => state.fetchKeys(),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }
                if (state.keys.isEmpty) {
                  return const Center(
                    child: Text(
                      'No keys found.',
                      style: TextStyle(color: Color(0xFF6B7280)),
                    ),
                  );
                }
                return ListView.separated(
                  itemCount: state.keys.length + 1,
                  separatorBuilder: (context, index) => const Divider(
                    height: 1,
                    thickness: 1,
                    color: Color(0xFFE4E7EA),
                  ),
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      return _buildTableHeader();
                    }
                    return _buildTableRow(context, state.keys[index - 1], index - 1);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTableHeader() {
    return Container(
      color: const Color(0xFFFAFAFA),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: Row(
        children: const [
          SizedBox(
            width: 56,
            child: Text(
              'NO',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.66,
                color: Color(0xFF6B7280),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(
              'ROLE',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.66,
                color: Color(0xFF6B7280),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(
              'STATUS',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.66,
                color: Color(0xFF6B7280),
              ),
            ),
          ),
          SizedBox(
            width: 140,
            child: Text(
              'ACTION',
              textAlign: TextAlign.right,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.66,
                color: Color(0xFF6B7280),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTableRow(BuildContext context, AccessKeyModel keyModel, int index) {
    final String roleName = keyModel.roleName;
    Color roleColor = const Color(0xFF6B7280);
    if (roleName.toLowerCase().contains('insurance')) roleColor = const Color(0xFF5B8DEF);
    else if (roleName.toLowerCase().contains('owner')) roleColor = const Color(0xFFB4770A);
    else if (roleName.toLowerCase().contains('mechanic')) roleColor = const Color(0xFF8B6FE0);
    else if (roleName.toLowerCase().contains('admin')) roleColor = const Color(0xFFC4453A);

    return InkWell(
      onTap: () {}, // For hover effect if supported
      hoverColor: const Color(0xFFFBFBFB),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        child: Row(
          children: [
            // No
            SizedBox(
              width: 56,
              child: Text(
                (index + 1).toString().padLeft(2, '0'),
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12.5,
                  color: Color(0xFF6B7280),
                ),
              ),
            ),
            // Role
            Expanded(
              flex: 2,
              child: Row(
                children: [
                  Container(
                    width: 7,
                    height: 7,
                    decoration: BoxDecoration(
                      color: roleColor,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 9),
                  Text(
                    roleName,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF1C2024),
                    ),
                  ),
                ],
              ),
            ),
            // Status
            Expanded(
              flex: 2,
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: keyModel.active
                          ? const Color.fromRGBO(47, 147, 102, 0.10)
                          : const Color.fromRGBO(196, 69, 58, 0.08),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: keyModel.active
                                ? const Color(0xFF2F9366)
                                : const Color(0xFFC4453A),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          keyModel.active ? 'Active' : 'Not active',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: keyModel.active
                                ? const Color(0xFF2F9366)
                                : const Color(0xFFC4453A),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            // Action
            SizedBox(
              width: 140,
              child: Align(
                alignment: Alignment.centerRight,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 100,
                      child: TextButton(
                        onPressed: () {
                          context.read<AdminState>().toggleKeyStatus(keyModel.id, keyModel.active);
                        },
                        style: TextButton.styleFrom(
                          backgroundColor: keyModel.active ? const Color.fromARGB(22, 255, 0, 0) : const Color(0xFF2F9366),
                          foregroundColor: keyModel.active ? const Color(0xFFC4453A) : const Color(0xFFFFFFFF),
                          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(
                              color: keyModel.active ? const Color.fromRGBO(196, 69, 58, 0.08) : Colors.transparent,
                            ),
                          ),
                          minimumSize: Size.zero,
                        ),
                        child: Text(
                          keyModel.active ? 'Deactivate' : 'Activate',
                          style: const TextStyle(
                            fontSize: 12.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.delete_outline, size: 18),
                      color: const Color(0xFFC4453A),
                      splashRadius: 20,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                      tooltip: 'Delete Key',
                      onPressed: () async {
                        final confirm = await showDialog<bool>(
                          context: context,
                          builder: (ctx) => AlertDialog(
                            title: const Text('Delete Access Key'),
                            content: const Text('Are you sure you want to permanently delete this access key?'),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(ctx, false),
                                child: const Text('Cancel'),
                              ),
                              TextButton(
                                onPressed: () => Navigator.pop(ctx, true),
                                style: TextButton.styleFrom(foregroundColor: Colors.red),
                                child: const Text('Delete'),
                              ),
                            ],
                          ),
                        );
                        if (confirm == true && context.mounted) {
                          context.read<AdminState>().deleteKey(keyModel.id);
                        }
                      },
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
