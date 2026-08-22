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
  // Anything narrower than this is treated as "mobile" layout.
  static const double _mobileBreakpoint = 700;

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
          LayoutBuilder(
            builder: (context, constraints) {
              final bool isMobile = constraints.maxWidth < _mobileBreakpoint;
              return Center(
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    maxWidth: isMobile ? double.infinity : 760,
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: isMobile ? 12 : 20,
                      vertical: isMobile ? 20 : 32,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _buildTopbar(context, isMobile),
                        SizedBox(height: isMobile ? 18 : 28),
                        Expanded(
                          child: _buildCard(context, isMobile),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTopbar(BuildContext context, bool isMobile) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Row(
            children: [
              Container(
                width: isMobile ? 34 : 40,
                height: isMobile ? 34 : 40,
                decoration: BoxDecoration(
                  color: const Color.fromRGBO(180, 119, 10, 0.10),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.vpn_key_rounded,
                  color: const Color(0xFFB4770A),
                  size: isMobile ? 16 : 19,
                ),
              ),
              const SizedBox(width: 12),
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome, Admin',
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: isMobile ? 15.5 : 18,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF1C2024),
                        letterSpacing: -0.18,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Manage account access below',
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: isMobile ? 11.5 : 12.5,
                        color: const Color(0xFF6B7280),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        OutlinedButton.icon(
          onPressed: () => context.read<AuthState>().logout(),
          style: OutlinedButton.styleFrom(
            backgroundColor: const Color(0xFFFFFFFF),
            foregroundColor: const Color(0xFF1C2024),
            side: const BorderSide(color: Color(0xFFE4E7EA)),
            padding: EdgeInsets.symmetric(
              horizontal: isMobile ? 12 : 16,
              vertical: isMobile ? 14 : 20,
            ),
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
          // Save horizontal space on small screens by dropping the label.
          label: isMobile ? const SizedBox.shrink() : const Text('Log out'),
        ),
      ],
    );
  }

  Widget _buildCard(BuildContext context, bool isMobile) {
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
            padding: EdgeInsets.fromLTRB(
              isMobile ? 16 : 24,
              isMobile ? 16 : 20,
              isMobile ? 16 : 24,
              isMobile ? 14 : 16,
            ),
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
                    children: [
                      Text(
                        'User accounts',
                        style: TextStyle(
                          fontSize: isMobile ? 13.5 : 14.5,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF1C2024),
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        'Activate or deactivate access by role',
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontSize: isMobile ? 11.5 : 12.5,
                          color: const Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _showCreateKeyDialog,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFB4770A),
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(
                      horizontal: isMobile ? 12 : 15,
                      vertical: isMobile ? 14 : 20,
                    ),
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
                  label: isMobile
                      ? const SizedBox.shrink()
                      : const Text('Create key'),
                ),
              ],
            ),
          ),
          // Table / List
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
                        Text(state.errorMessage!,
                            style: const TextStyle(color: Colors.red)),
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

                if (isMobile) {
                  // Stacked card layout — avoids cramming a multi-column
                  // table into a narrow screen.
                  return ListView.separated(
                    itemCount: state.keys.length,
                    separatorBuilder: (context, index) => const Divider(
                      height: 1,
                      thickness: 1,
                      color: Color(0xFFE4E7EA),
                    ),
                    itemBuilder: (context, index) {
                      return _buildMobileKeyCard(
                          context, state.keys[index], index);
                    },
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
                    return _buildTableRow(
                        context, state.keys[index - 1], index - 1);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Color _roleColor(String roleName) {
    final String lower = roleName.toLowerCase();
    if (lower.contains('insurance')) return const Color(0xFF5B8DEF);
    if (lower.contains('owner')) return const Color(0xFFB4770A);
    if (lower.contains('mechanic')) return const Color(0xFF8B6FE0);
    if (lower.contains('admin')) return const Color(0xFFC4453A);
    return const Color(0xFF6B7280);
  }

  Future<void> _confirmAndDelete(
      BuildContext context, AccessKeyModel keyModel) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Access Key'),
        content: const Text(
            'Are you sure you want to permanently delete this access key?'),
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
  }

  Widget _statusBadge(bool active) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: active
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
              color: active ? const Color(0xFF2F9366) : const Color(0xFFC4453A),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            active ? 'Active' : 'Not active',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: active ? const Color(0xFF2F9366) : const Color(0xFFC4453A),
            ),
          ),
        ],
      ),
    );
  }

  // ---- Mobile: stacked card row ----
  Widget _buildMobileKeyCard(
      BuildContext context, AccessKeyModel keyModel, int index) {
    final String roleName = keyModel.roleName;
    final Color roleColor = _roleColor(roleName);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                (index + 1).toString().padLeft(2, '0'),
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 11.5,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(width: 10),
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  color: roleColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  roleName,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1C2024),
                  ),
                ),
              ),
              _statusBadge(keyModel.active),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextButton(
                  onPressed: () {
                    context
                        .read<AdminState>()
                        .toggleKeyStatus(keyModel.id, keyModel.active);
                  },
                  style: TextButton.styleFrom(
                    backgroundColor: keyModel.active
                        ? const Color.fromARGB(22, 255, 0, 0)
                        : const Color(0xFF2F9366),
                    foregroundColor: keyModel.active
                        ? const Color(0xFFC4453A)
                        : const Color(0xFFFFFFFF),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: keyModel.active
                            ? const Color.fromRGBO(196, 69, 58, 0.08)
                            : Colors.transparent,
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
                constraints:
                    const BoxConstraints(minWidth: 36, minHeight: 36),
                tooltip: 'Delete Key',
                onPressed: () => _confirmAndDelete(context, keyModel),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ---- Desktop: table header ----
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

  // ---- Desktop: table row ----
  Widget _buildTableRow(
      BuildContext context, AccessKeyModel keyModel, int index) {
    final String roleName = keyModel.roleName;
    final Color roleColor = _roleColor(roleName);

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
                  Flexible(
                    child: Text(
                      roleName,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF1C2024),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Status
            Expanded(
              flex: 2,
              child: Row(
                children: [_statusBadge(keyModel.active)],
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
                          context
                              .read<AdminState>()
                              .toggleKeyStatus(keyModel.id, keyModel.active);
                        },
                        style: TextButton.styleFrom(
                          backgroundColor: keyModel.active
                              ? const Color.fromARGB(22, 255, 0, 0)
                              : const Color(0xFF2F9366),
                          foregroundColor: keyModel.active
                              ? const Color(0xFFC4453A)
                              : const Color(0xFFFFFFFF),
                          padding: const EdgeInsets.symmetric(
                              vertical: 20, horizontal: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(
                              color: keyModel.active
                                  ? const Color.fromRGBO(196, 69, 58, 0.08)
                                  : Colors.transparent,
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
                      constraints:
                          const BoxConstraints(minWidth: 32, minHeight: 32),
                      tooltip: 'Delete Key',
                      onPressed: () => _confirmAndDelete(context, keyModel),
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